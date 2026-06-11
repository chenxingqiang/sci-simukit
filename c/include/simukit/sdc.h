#ifndef SIMUKIT_SDC_H
#define SIMUKIT_SDC_H

#include "simukit/cp2k_out.h"

typedef struct {
    int n_molecules;
    char dopant[SIMUKIT_DOPANT_MAX];
    double strain_pct;
} simukit_size_meta_t;

typedef struct {
    char property[64];
    int n_molecules;
    char dopant[SIMUKIT_DOPANT_MAX];
    double strain_pct;
    double synergy_S;
    double reference;
    double combined;
    double strain_only_delta;
    double doping_only_delta;
} simukit_synergy_record_t;

#define SIMUKIT_SDC_MAX_RECORDS 256

typedef struct {
    simukit_synergy_record_t records[SIMUKIT_SDC_MAX_RECORDS];
    size_t count;
    int n_parsed;
    int n_converged;
} simukit_sdc_report_t;

/* Parse size_Nx60_{dopant}_{pos|neg}Xpct filename. Returns 0 on success. */
int simukit_parse_size_filename(const char *basename, simukit_size_meta_t *meta);

/*
 * Scan directory for size_*.out, compute energy-per-atom synergy at strain_pct.
 * property: "energy_per_atom_ha" (only supported in v0.1).
 */
int simukit_sdc_analyze_dir(const char *inputs_dir, double strain_pct,
                            simukit_sdc_report_t *report);

/* Write minimal JSON report to path. */
int simukit_sdc_write_json(const char *path, const simukit_sdc_report_t *report,
                           double strain_pct, const char *inputs_dir);

#endif
