source("functions_counts.R")
source("functions_levels.R")
source("functions.R")

## -----------------------------
## Categorised Log Sample
plot_categorised_sample(logsSample)
## -----------------------------
## Log Levels
# plot_levels("ds", "file", "Print", 1e4)
# plot_levels("non-ds", "file", "Print", 1e4)
# plot_levels("ds", "file", "CRITICAL", 1e2)
# plot_levels("non-ds", "file", "CRITICAL", 1e2)
# plot_levels("ds", "file", "ERROR", 1e3)
# plot_levels("non-ds", "file", "ERROR", 1e3)
# plot_levels("ds", "file", "WARNING", 1e3)
# plot_levels("non-ds", "file", "WARNING", 1e3)
# plot_levels("ds", "file", "INFO", 1e3)
# plot_levels("non-ds", "file", "INFO", 1e3)
# plot_levels("ds", "file", "DEBUG", 1e3)
# plot_levels("non-ds", "file", "DEBUG", 1e3)
## -----------------------------
## File
plot_scope_count("ds", "file")
plot_scope_count("non-ds", "file")
# plot_loc("ds", "file")
# plot_loc("non-ds", "file")
# plot_log_count("ds", "file")
# plot_log_count("non-ds", "file")
plot_log_distribution("file")
plot_log_density("file")
## -----------------------------
# Class
# plot_scope_count("ds", "class")
# plot_scope_count("non-ds", "class")
# plot_loc("ds", "class")
# plot_loc("non-ds", "class")
# plot_log_count("ds", "class")
# plot_log_count("non-ds", "class")
# plot_log_distribution("class")
# plot_log_density("class")
## -----------------------------
# Module
# plot_scope_count("ds", "module")
# plot_scope_count("non-ds", "module")
# plot_loc("ds", "module")
# plot_loc("non-ds", "module")
# plot_log_count("ds", "module")
# plot_log_count("non-ds", "module")
# plot_log_distribution("module")
# plot_log_density("module")
## -----------------------------
# function
# plot_scope_count("ds", "function")
# plot_scope_count("non-ds", "function")
# plot_loc("ds", "function")
# plot_loc("non-ds", "function")
# plot_log_count("ds", "function")
# plot_log_count("non-ds", "function")
# plot_log_distribution("function")
# plot_log_density("function")
## -----------------------------
# # method
# plot_scope_count("ds", "method")
# plot_scope_count("non-ds", "method")
# plot_loc("ds", "method")
# plot_loc("non-ds", "method")
# plot_log_count("ds", "method")
# plot_log_count("non-ds", "method")
# plot_log_distribution("method")
# plot_log_density("method")
