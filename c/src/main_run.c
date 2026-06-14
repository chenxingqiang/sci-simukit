#include "simukit/simukit.h"
#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *default_pending[] = {
    "size_2x60_pristine_pos0pct", "size_2x60_pristine_pos3pct", "size_4x60_P_pos3pct",
    "size_6x60_B_pos3pct",         "size_6x60_N_pos3pct",       "size_8x60_B_pos0pct",
    "size_8x60_B_pos3pct",         "size_8x60_N_pos3pct",       "size_8x60_P_pos0pct",
    "size_8x60_P_pos3pct",         "size_8x60_pristine_pos0pct", "size_8x60_pristine_pos3pct",
    NULL};

static void usage(const char *prog) {
    fprintf(stderr,
            "Usage: %s [options] <inputs_dir>\n"
            "  --cp2k PATH     CP2K binary (default: CP2K_BIN or autodetect)\n"
            "  --data PATH     CP2K_DATA directory\n"
            "  --log PATH      Append log (default: experiments/local_run.log)\n"
            "  --one BASE      Run single task basename (no .inp suffix)\n"
            "  --exp8-sp       Also run geoopt_pristine_sp after Exp10 list\n"
            "  Default inputs: experiments/exp_10_size_scaling/inputs\n",
            prog);
}

static int run_task(const char *inputs_dir, const char *base, simukit_run_config_t *cfg) {
    char inp[SIMUKIT_PATH_MAX];
    char out[SIMUKIT_PATH_MAX];
    int rc;

    snprintf(inp, sizeof(inp), "%s/%s.inp", inputs_dir, base);
    snprintf(out, sizeof(out), "%s/%s.out", inputs_dir, base);
    cfg->nprocs = simukit_cp2k_suggest_nprocs(base);
    rc = simukit_cp2k_run_job(inp, out, cfg);
    return rc;
}

int main(int argc, char **argv) {
    simukit_run_config_t cfg;
    const char *inputs_dir = "experiments/exp_10_size_scaling/inputs";
    const char *one_task = NULL;
    int exp8_sp = 0;
    int failures = 0;

    memset(&cfg, 0, sizeof(cfg));
    simukit_strlcpy(cfg.log_path, "experiments/local_run.log", sizeof(cfg.log_path));
    if (getenv("CP2K_DATA")) {
        simukit_strlcpy(cfg.cp2k_data, getenv("CP2K_DATA"), sizeof(cfg.cp2k_data));
    } else {
        simukit_strlcpy(cfg.cp2k_data, "/opt/homebrew/share/cp2k/data", sizeof(cfg.cp2k_data));
    }

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--cp2k") == 0 && i + 1 < argc) {
            simukit_strlcpy(cfg.cp2k_bin, argv[++i], sizeof(cfg.cp2k_bin));
        } else if (strcmp(argv[i], "--data") == 0 && i + 1 < argc) {
            simukit_strlcpy(cfg.cp2k_data, argv[++i], sizeof(cfg.cp2k_data));
        } else if (strcmp(argv[i], "--log") == 0 && i + 1 < argc) {
            simukit_strlcpy(cfg.log_path, argv[++i], sizeof(cfg.log_path));
        } else if (strcmp(argv[i], "--one") == 0 && i + 1 < argc) {
            one_task = argv[++i];
        } else if (strcmp(argv[i], "--exp8-sp") == 0) {
            exp8_sp = 1;
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            usage(argv[0]);
            return 0;
        } else if (argv[i][0] != '-') {
            inputs_dir = argv[i];
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (simukit_cp2k_resolve_binary(&cfg) != 0) {
        fprintf(stderr, "CP2K binary not found; set CP2K_BIN or pass --cp2k\n");
        return 1;
    }

    printf("simukit-run %s: cp2k=%s npolicy=size-scaling sequential max_np=%d (fraction=%s)\n",
           SIMUKIT_VERSION, cfg.cp2k_bin, simukit_cp2k_max_nprocs(),
           getenv("SIMUKIT_CPU_FRACTION") ? getenv("SIMUKIT_CPU_FRACTION") : "0.67");

    if (one_task) {
        if (run_task(inputs_dir, one_task, &cfg) != 0) {
            failures++;
        }
    } else {
        for (size_t i = 0; default_pending[i]; i++) {
            if (run_task(inputs_dir, default_pending[i], &cfg) != 0) {
                failures++;
            }
        }
    }

    if (exp8_sp) {
        const char *exp8 = "experiments/exp_8_geometry_opt/inputs";
        if (run_task(exp8, "geoopt_pristine_sp", &cfg) != 0) {
            failures++;
        }
    }

    printf("simukit-run finished: failures=%d\n", failures);
    return failures > 0 ? 1 : 0;
}
