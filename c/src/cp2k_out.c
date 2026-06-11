#include "simukit/cp2k_out.h"
#include "util.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool simukit_cp2k_is_converged(const simukit_cp2k_result_t *r) {
    /* Match batch scripts: SCF run converged + parsable total energy. */
    return r && r->converged && r->has_energy;
}

static int parse_energy_line(const char *line, double *energy_ha) {
    const char *p;
    if (strstr(line, "ENERGY| Total FORCE_EVAL") != NULL) {
        p = strrchr(line, ':');
        if (p && sscanf(p + 1, " %lf", energy_ha) == 1) {
            return 1;
        }
    }
    if (strstr(line, "Total energy:") != NULL) {
        p = strchr(line, ':');
        if (p && sscanf(p + 1, " %lf", energy_ha) == 1) {
            return 1;
        }
    }
    return 0;
}

static void parse_mo_block(const char *content, int n_atoms, simukit_cp2k_result_t *out) {
    const char *p;
    const char *line;
    double eigenvalues[8192];
    int n_ev = 0;
    int in_block = 0;
    int n_electrons;
    int homo_idx;

    p = content;
    while ((line = strchr(p, '\n')) != NULL) {
        size_t len = (size_t)(line - p);
        char buf[512];

        if (len >= sizeof(buf)) {
            p = line + 1;
            continue;
        }
        memcpy(buf, p, len);
        buf[len] = '\0';

        if (strstr(buf, "MO EIGENVALUES") != NULL ||
            (strstr(buf, "Occupation") != NULL && strstr(buf, "Eigenvalues") != NULL)) {
            in_block = 1;
            n_ev = 0;
            p = line + 1;
            continue;
        }

        if (in_block) {
            char *tok;
            char tmp[512];
            if (len == 0 || strstr(buf, "Fermi") != NULL || simukit_starts_with(buf, " ---")) {
                break;
            }
            simukit_strlcpy(tmp, buf, sizeof(tmp));
            tok = strtok(tmp, " \t");
            while (tok && n_ev < (int)(sizeof(eigenvalues) / sizeof(eigenvalues[0]))) {
                char *end = NULL;
                double val = strtod(tok, &end);
                if (end != tok) {
                    eigenvalues[n_ev++] = val;
                }
                tok = strtok(NULL, " \t");
            }
        }
        p = line + 1;
    }

    if (n_ev == 0 || n_atoms <= 0) {
        return;
    }

    n_electrons = n_atoms * 4;
    homo_idx = n_electrons / 2 - 1;
    if (homo_idx < 0 || homo_idx >= n_ev) {
        return;
    }

    out->homo_ev = eigenvalues[homo_idx] * SIMUKIT_HA_TO_EV;
    if (homo_idx + 1 < n_ev) {
        out->lumo_ev = eigenvalues[homo_idx + 1] * SIMUKIT_HA_TO_EV;
        out->bandgap_ev = out->lumo_ev - out->homo_ev;
    }
    if (homo_idx - 1 >= 0) {
        out->j_coupling_meV =
            fabs(out->homo_ev - eigenvalues[homo_idx - 1] * SIMUKIT_HA_TO_EV) / 2.0 * 1000.0;
    }
    out->has_mo = true;
}

int simukit_cp2k_parse_file(const char *path, simukit_cp2k_result_t *out) {
    char *content;
    const char *line;
    const char *p;
    size_t len;

    if (!path || !out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));
    simukit_strlcpy(out->path, path, sizeof(out->path));

    content = simukit_read_file(path, &len);
    if (!content) {
        return -2;
    }

    if (strstr(content, "SCF run converged") != NULL) {
        out->converged = true;
    }
    if (strstr(content, "PROGRAM ENDED") != NULL) {
        out->program_ended = true;
    }

    p = content;
    while ((line = strchr(p, '\n')) != NULL) {
        char buf[1024];
        size_t ll = (size_t)(line - p);
        if (ll < sizeof(buf)) {
            memcpy(buf, p, ll);
            buf[ll] = '\0';
            if (strstr(buf, "- Atoms:") != NULL) {
                sscanf(buf, " - Atoms: %d", &out->n_atoms);
            }
            if (strstr(buf, "Number of atoms") != NULL) {
                int na = 0;
                if (sscanf(buf, " Number of atoms %d", &na) == 1 ||
                    sscanf(buf, " Number of atoms: %d", &na) == 1) {
                    out->n_atoms = na;
                }
            }
            if (parse_energy_line(buf, &out->total_energy_ha)) {
                out->has_energy = true;
            }
        }
        p = line + 1;
    }

    if (out->has_energy && out->n_atoms > 0) {
        out->energy_per_atom_ha = out->total_energy_ha / (double)out->n_atoms;
    }

    parse_mo_block(content, out->n_atoms, out);
    free(content);
    return 0;
}

#ifdef SIMUKIT_TEST_CP2K_OUT
#include <assert.h>

int main(void) {
    simukit_cp2k_result_t r;
    assert(simukit_cp2k_parse_file("test.out", &r) != 0 || 1);
    return 0;
}
#endif
