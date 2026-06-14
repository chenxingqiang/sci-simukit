#include "simukit/cp2k_run.h"
#include "util.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static int file_exists(const char *path) {
    struct stat st;
    return path && stat(path, &st) == 0;
}

static int append_log(const char *log_path, const char *msg) {
    FILE *f;
    time_t now;
    char tbuf[64];

    if (!log_path || !log_path[0]) {
        return 0;
    }
    f = fopen(log_path, "a");
    if (!f) {
        return -1;
    }
    now = time(NULL);
    strftime(tbuf, sizeof(tbuf), "%Y-%m-%d %H:%M:%S", localtime(&now));
    fprintf(f, "%s %s\n", tbuf, msg);
    fclose(f);
    return 0;
}

int simukit_cp2k_resolve_binary(simukit_run_config_t *cfg) {
    const char *env;
    const char *candidates[] = {
        "/opt/homebrew/bin/cp2k.psmp",
        "/usr/local/bin/cp2k.psmp",
        "/opt/cp2k/exe/local/cp2k.psmp",
        NULL};

    if (!cfg) {
        return -1;
    }
    if (cfg->cp2k_bin[0] && file_exists(cfg->cp2k_bin)) {
        return 0;
    }
    env = getenv("CP2K_BIN");
    if (env && file_exists(env)) {
        simukit_strlcpy(cfg->cp2k_bin, env, sizeof(cfg->cp2k_bin));
        return 0;
    }
    for (size_t i = 0; candidates[i]; i++) {
        if (file_exists(candidates[i])) {
            simukit_strlcpy(cfg->cp2k_bin, candidates[i], sizeof(cfg->cp2k_bin));
            return 0;
        }
    }
    return -2;
}

static int detect_ncpu(void) {
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    return n > 0 ? (int)n : 4;
}

int simukit_cp2k_max_nprocs(void) {
    const char *frac_env = getenv("SIMUKIT_CPU_FRACTION");
    const char *max_env = getenv("SIMUKIT_MAX_CORES");
    double frac = 0.67;
    int max_cores;

    if (frac_env) {
        frac = strtod(frac_env, NULL);
    }
    if (frac <= 0.0 || frac > 1.0) {
        frac = 0.67;
    }
    max_cores = (int)((double)detect_ncpu() * frac);
    if (max_cores < 1) {
        max_cores = 1;
    }
    if (max_env) {
        int override = (int)strtol(max_env, NULL, 10);
        if (override > 0) {
            max_cores = override;
        }
    }
    return max_cores;
}

int simukit_cp2k_effective_nprocs(int suggested) {
    int cap = simukit_cp2k_max_nprocs();
    if (suggested < 1) {
        suggested = 1;
    }
    return suggested > cap ? cap : suggested;
}

int simukit_cp2k_suggest_nprocs(const char *task_basename) {
    int suggested = 4;

    if (!task_basename) {
        return simukit_cp2k_effective_nprocs(suggested);
    }
    if (simukit_starts_with(task_basename, "size_8x60_")) {
        suggested = 10;
    } else if (simukit_starts_with(task_basename, "size_6x60_")) {
        suggested = 8;
    } else if (simukit_starts_with(task_basename, "size_4x60_")) {
        suggested = 6;
    }
    return simukit_cp2k_effective_nprocs(suggested);
}

static int split_dir_base(const char *path, char *dir, size_t dir_sz, char *base, size_t base_sz) {
    const char *slash;
    if (!path) {
        return -1;
    }
    slash = strrchr(path, '/');
    if (!slash) {
        simukit_strlcpy(dir, ".", dir_sz);
        simukit_strlcpy(base, path, base_sz);
        return 0;
    }
    if ((size_t)(slash - path) + 1 > dir_sz) {
        return -1;
    }
    memcpy(dir, path, (size_t)(slash - path));
    dir[slash - path] = '\0';
    simukit_strlcpy(base, slash + 1, base_sz);
    return 0;
}

int simukit_cp2k_run_job(const char *inp_path, const char *out_path,
                         const simukit_run_config_t *cfg) {
    pid_t pid;
    char workdir[SIMUKIT_PATH_MAX];
    char inp_base[SIMUKIT_PATH_MAX];
    char out_base[SIMUKIT_PATH_MAX];
    char logmsg[512];
    simukit_cp2k_result_t parsed;
    int status;
    char npbuf[16];

    if (!inp_path || !out_path || !cfg) {
        return -1;
    }
    if (simukit_cp2k_parse_file(out_path, &parsed) == 0 && simukit_cp2k_is_converged(&parsed)) {
        return 0;
    }
    if (split_dir_base(inp_path, workdir, sizeof(workdir), inp_base, sizeof(inp_base)) != 0) {
        return -2;
    }
    {
        char out_dir[SIMUKIT_PATH_MAX];
        if (split_dir_base(out_path, out_dir, sizeof(out_dir), out_base, sizeof(out_base)) != 0) {
            return -2;
        }
        (void)out_dir;
    }

    snprintf(logmsg, sizeof(logmsg), "START: %s (np=%d)", inp_base, cfg->nprocs > 0 ? cfg->nprocs : 4);
    append_log(cfg->log_path, logmsg);

    pid = fork();
    if (pid < 0) {
        return -3;
    }
    if (pid == 0) {
        char *mpirun = "/opt/homebrew/bin/mpirun";
        char *mpirun_fallback = "mpirun";
        char *mpirun_path = mpirun;
        if (!file_exists(mpirun_path)) {
            mpirun_path = mpirun_fallback;
        }
        snprintf(npbuf, sizeof(npbuf), "%d", cfg->nprocs > 0 ? cfg->nprocs : 4);
        if (chdir(workdir) != 0) {
            _exit(127);
        }
        if (cfg->cp2k_data[0]) {
            setenv("CP2K_DATA", cfg->cp2k_data, 1);
        }
        if (!getenv("OMP_NUM_THREADS")) {
            setenv("OMP_NUM_THREADS", "1", 1);
        }
        if (!getenv("OMP_STACKSIZE")) {
            setenv("OMP_STACKSIZE", "512M", 1);
        }
        execlp(mpirun_path, mpirun_path, "-np", npbuf, cfg->cp2k_bin, "-i", inp_base, "-o", out_base,
               (char *)NULL);
        /* fallback: direct cp2k without mpi */
        execlp(cfg->cp2k_bin, cfg->cp2k_bin, "-i", inp_base, "-o", out_base, (char *)NULL);
        _exit(127);
    }

    if (waitpid(pid, &status, 0) < 0) {
        return -4;
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        snprintf(logmsg, sizeof(logmsg), "FAIL: %s (cp2k exit %d)", inp_base,
                 WIFEXITED(status) ? WEXITSTATUS(status) : -1);
        append_log(cfg->log_path, logmsg);
        return -5;
    }

    if (simukit_cp2k_parse_file(out_path, &parsed) == 0 && simukit_cp2k_is_converged(&parsed)) {
        snprintf(logmsg, sizeof(logmsg), "DONE: %s", inp_base);
        append_log(cfg->log_path, logmsg);
        return 0;
    }

    snprintf(logmsg, sizeof(logmsg), "FAIL: %s (no SCF convergence)", inp_base);
    append_log(cfg->log_path, logmsg);
    return 1;
}
