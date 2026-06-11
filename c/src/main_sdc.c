#include "simukit/simukit.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void usage(const char *prog) {
    fprintf(stderr,
            "Usage: %s [--strain PCT] [--out JSON] <exp10_inputs_dir>\n"
            "  Default strain: 3.0\n"
            "  Default out:    experiments/analysis/sdc/sdc_exp10_results.json\n",
            prog);
}

int main(int argc, char **argv) {
    const char *inputs_dir = NULL;
    const char *out_json = "experiments/analysis/sdc/sdc_exp10_results.json";
    double strain_pct = 3.0;
    simukit_sdc_report_t report;
    int rc;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--strain") == 0 && i + 1 < argc) {
            strain_pct = atof(argv[++i]);
        } else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) {
            out_json = argv[++i];
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            usage(argv[0]);
            return 0;
        } else if (!inputs_dir) {
            inputs_dir = argv[i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (!inputs_dir) {
        inputs_dir = "experiments/exp_10_size_scaling/inputs";
    }

    rc = simukit_sdc_analyze_dir(inputs_dir, strain_pct, &report);
    if (rc != 0) {
        fprintf(stderr, "simukit_sdc_analyze_dir failed: %d\n", rc);
        return 1;
    }

    rc = simukit_sdc_write_json(out_json, &report, strain_pct, inputs_dir);
    if (rc != 0) {
        fprintf(stderr, "simukit_sdc_write_json failed: %d\n", rc);
        return 1;
    }

    printf("simukit-sdc %s: parsed=%d converged=%d synergy_records=%zu\n", SIMUKIT_VERSION,
           report.n_parsed, report.n_converged, report.count);
    for (size_t i = 0; i < report.count; i++) {
        const simukit_synergy_record_t *r = &report.records[i];
        printf("  n=%d %s S=%.4e Ha/atom\n", r->n_molecules, r->dopant, r->synergy_S);
    }
    return 0;
}
