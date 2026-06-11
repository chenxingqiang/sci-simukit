#ifndef SIMUKIT_CP2K_OUT_H
#define SIMUKIT_CP2K_OUT_H

#include <stdbool.h>
#include <stddef.h>

#define SIMUKIT_PATH_MAX 4096
#define SIMUKIT_DOPANT_MAX 16

#define SIMUKIT_HA_TO_EV 27.211386245988

typedef struct {
    char path[SIMUKIT_PATH_MAX];
    bool converged;
    bool program_ended;
    bool has_energy;
    int n_atoms;
    double total_energy_ha;
    double energy_per_atom_ha;
    bool has_mo;
    double homo_ev;
    double lumo_ev;
    double bandgap_ev;
    double j_coupling_meV;
} simukit_cp2k_result_t;

/* Parse a CP2K .out file into result (zero-initialized on input). */
int simukit_cp2k_parse_file(const char *path, simukit_cp2k_result_t *out);

/* True when SCF converged (same gate as batch scripts). */
bool simukit_cp2k_is_converged(const simukit_cp2k_result_t *r);

#endif
