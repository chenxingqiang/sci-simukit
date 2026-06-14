#ifndef SIMUKIT_CP2K_RUN_H
#define SIMUKIT_CP2K_RUN_H

#include "simukit/cp2k_out.h"
#include <stddef.h>

typedef struct {
    char cp2k_bin[SIMUKIT_PATH_MAX];
    char cp2k_data[SIMUKIT_PATH_MAX];
    char log_path[SIMUKIT_PATH_MAX];
    int nprocs;
} simukit_run_config_t;

/* Resolve CP2K binary: config->cp2k_bin, then $CP2K_BIN, then PATH. */
int simukit_cp2k_resolve_binary(simukit_run_config_t *cfg);

/*
 * Run one CP2K job: mpirun -np nprocs cp2k -i inp -o out in inp's directory.
 * Returns 0 on success and converged output; 1 if ran but not converged; negative on error.
 */
int simukit_cp2k_run_job(const char *inp_path, const char *out_path,
                         const simukit_run_config_t *cfg);

/* Suggested MPI ranks from task basename (Exp10 size scaling). */
int simukit_cp2k_suggest_nprocs(const char *task_basename);

int simukit_cp2k_max_nprocs(void);
int simukit_cp2k_effective_nprocs(int suggested);

#endif
