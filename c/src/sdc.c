#include "simukit/sdc.h"
#include "simukit/simukit.h"
#include "util.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char key[128];
    simukit_cp2k_result_t res;
    simukit_size_meta_t meta;
    int valid;
} sdc_entry_t;

#define SDC_MAX_ENTRIES 128

static void make_key(int n, const char *dopant, double strain, char *key, size_t key_sz) {
    snprintf(key, key_sz, "n%d_%s_eps%+.0f", n, dopant, strain);
}

static sdc_entry_t *find_entry(sdc_entry_t *entries, int n_entries, const char *key) {
    for (int i = 0; i < n_entries; i++) {
        if (entries[i].valid && strcmp(entries[i].key, key) == 0) {
            return &entries[i];
        }
    }
    return NULL;
}

static int insert_entry(sdc_entry_t *entries, int *n_entries, const char *key,
                        const simukit_size_meta_t *meta, const simukit_cp2k_result_t *res) {
    sdc_entry_t *e;
    if (*n_entries >= SDC_MAX_ENTRIES) {
        return -1;
    }
    e = &entries[(*n_entries)++];
    simukit_strlcpy(e->key, key, sizeof(e->key));
    e->meta = *meta;
    e->res = *res;
    e->valid = 1;
    return 0;
}

int simukit_parse_size_filename(const char *basename, simukit_size_meta_t *meta) {
    int n, val;
    char sign[8];
    char dopant_raw[32];

    if (!basename || !meta) {
        return -1;
    }
    memset(meta, 0, sizeof(*meta));

    if (sscanf(basename, "size_%dx60_%31[^_]_%7[^0-9]%d", &n, dopant_raw, sign, &val) != 4) {
        return -2;
    }

    meta->n_molecules = n;
    if (strcmp(dopant_raw, "pristine") == 0) {
        simukit_strlcpy(meta->dopant, "pristine", sizeof(meta->dopant));
    } else if (strlen(dopant_raw) == 1 &&
               (dopant_raw[0] == 'B' || dopant_raw[0] == 'N' || dopant_raw[0] == 'P')) {
        simukit_strlcpy(meta->dopant, dopant_raw, sizeof(meta->dopant));
    } else {
        return -3;
    }

    if (strcmp(sign, "pos") == 0) {
        meta->strain_pct = (double)val;
    } else if (strcmp(sign, "neg") == 0) {
        meta->strain_pct = -(double)val;
    } else {
        return -4;
    }
    return 0;
}

static int get_epa(const simukit_cp2k_result_t *r, double *out) {
    if (!r || !r->has_energy || r->n_atoms <= 0) {
        return -1;
    }
    *out = r->energy_per_atom_ha;
    return 0;
}

int simukit_sdc_analyze_dir(const char *inputs_dir, double strain_pct,
                            simukit_sdc_report_t *report) {
    DIR *dir;
    struct dirent *ent;
    sdc_entry_t entries[SDC_MAX_ENTRIES];
    int n_entries = 0;
    static const char *dopants[] = {"B", "N", "P", NULL};
    int sizes[16];
    int n_sizes = 0;

    if (!inputs_dir || !report) {
        return -1;
    }
    memset(report, 0, sizeof(*report));
    memset(entries, 0, sizeof(entries));

    dir = opendir(inputs_dir);
    if (!dir) {
        return -2;
    }

    while ((ent = readdir(dir)) != NULL) {
        simukit_size_meta_t meta;
        simukit_cp2k_result_t res;
        char path[SIMUKIT_PATH_MAX];
        char key[128];
        char base[256];
        int found;

        if (!simukit_starts_with(ent->d_name, "size_") || !simukit_ends_with(ent->d_name, ".out")) {
            continue;
        }
        simukit_strlcpy(base, ent->d_name, sizeof(base));
        base[strlen(base) - 4] = '\0';

        if (simukit_parse_size_filename(base, &meta) != 0) {
            continue;
        }

        snprintf(path, sizeof(path), "%s/%s", inputs_dir, ent->d_name);
        report->n_parsed++;
        if (simukit_cp2k_parse_file(path, &res) != 0) {
            continue;
        }
        if (simukit_cp2k_is_converged(&res)) {
            report->n_converged++;
        }

        make_key(meta.n_molecules, meta.dopant, meta.strain_pct, key, sizeof(key));
        if (insert_entry(entries, &n_entries, key, &meta, &res) != 0) {
            closedir(dir);
            return -3;
        }

        found = 0;
        for (int j = 0; j < n_sizes; j++) {
            if (sizes[j] == meta.n_molecules) {
                found = 1;
                break;
            }
        }
        if (!found && n_sizes < 16) {
            sizes[n_sizes++] = meta.n_molecules;
        }
    }
    closedir(dir);

    for (int si = 0; si < n_sizes; si++) {
        int n = sizes[si];
        char key_ref[128], key_str[128];
        double p_ref, delta_str, epa;
        sdc_entry_t *ref, *strain_only;

        make_key(n, "pristine", 0.0, key_ref, sizeof(key_ref));
        make_key(n, "pristine", strain_pct, key_str, sizeof(key_str));

        ref = find_entry(entries, n_entries, key_ref);
        strain_only = find_entry(entries, n_entries, key_str);
        if (!ref || !strain_only || !simukit_cp2k_is_converged(&ref->res) ||
            !simukit_cp2k_is_converged(&strain_only->res)) {
            continue;
        }
        if (get_epa(&ref->res, &p_ref) != 0 || get_epa(&strain_only->res, &epa) != 0) {
            continue;
        }
        delta_str = epa - p_ref;

        for (int d = 0; dopants[d]; d++) {
            char key_d0[128], key_comb[128];
            sdc_entry_t *d0, *comb;
            simukit_synergy_record_t *rec;
            double p_d0, p_comb, delta_dop, delta_comb, synergy;

            make_key(n, dopants[d], 0.0, key_d0, sizeof(key_d0));
            make_key(n, dopants[d], strain_pct, key_comb, sizeof(key_comb));

            d0 = find_entry(entries, n_entries, key_d0);
            comb = find_entry(entries, n_entries, key_comb);
            if (!d0 || !comb || !simukit_cp2k_is_converged(&d0->res) ||
                !simukit_cp2k_is_converged(&comb->res)) {
                continue;
            }
            if (get_epa(&d0->res, &p_d0) != 0 || get_epa(&comb->res, &p_comb) != 0) {
                continue;
            }

            delta_dop = p_d0 - p_ref;
            delta_comb = p_comb - p_ref;
            synergy = delta_comb - (delta_str + delta_dop);

            if (report->count >= SIMUKIT_SDC_MAX_RECORDS) {
                return -4;
            }
            rec = &report->records[report->count++];
            simukit_strlcpy(rec->property, "energy_per_atom_ha", sizeof(rec->property));
            rec->n_molecules = n;
            simukit_strlcpy(rec->dopant, dopants[d], sizeof(rec->dopant));
            rec->strain_pct = strain_pct;
            rec->reference = p_ref;
            rec->combined = p_comb;
            rec->strain_only_delta = delta_str;
            rec->doping_only_delta = delta_dop;
            rec->synergy_S = synergy;
        }
    }

    return 0;
}

#include <sys/stat.h>

int simukit_sdc_write_json(const char *path, const simukit_sdc_report_t *report,
                           double strain_pct, const char *inputs_dir) {
    FILE *f;
    size_t i;
    char dirbuf[SIMUKIT_PATH_MAX];
    char *slash;

    if (!path || !report) {
        return -1;
    }
    simukit_strlcpy(dirbuf, path, sizeof(dirbuf));
    slash = strrchr(dirbuf, '/');
    if (slash) {
        *slash = '\0';
        mkdir(dirbuf, 0755);
    }
    f = fopen(path, "w");
    if (!f) {
        return -2;
    }

    fprintf(f, "{\n");
    fprintf(f, "  \"simukit_version\": \"%s\",\n", SIMUKIT_VERSION);
    fprintf(f, "  \"inputs_dir\": \"%s\",\n", inputs_dir ? inputs_dir : "");
    fprintf(f, "  \"strain_pct\": %.1f,\n", strain_pct);
    fprintf(f, "  \"n_parsed\": %d,\n", report->n_parsed);
    fprintf(f, "  \"n_converged\": %d,\n", report->n_converged);
    fprintf(f, "  \"synergy_energy_per_atom\": [\n");
    for (i = 0; i < report->count; i++) {
        const simukit_synergy_record_t *r = &report->records[i];
        fprintf(f,
                "    {\"n_molecules\": %d, \"dopant\": \"%s\", \"strain_pct\": %.1f, "
                "\"synergy_S\": %.12e, \"reference\": %.12e, \"combined\": %.12e, "
                "\"strain_only_delta\": %.12e, \"doping_only_delta\": %.12e}%s\n",
                r->n_molecules, r->dopant, r->strain_pct, r->synergy_S, r->reference,
                r->combined, r->strain_only_delta, r->doping_only_delta,
                (i + 1 < report->count) ? "," : "");
    }
    fprintf(f, "  ]\n}\n");
    fclose(f);
    return 0;
}
