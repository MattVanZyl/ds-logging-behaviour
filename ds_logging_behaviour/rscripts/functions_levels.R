# ==============================================================================
plot_levels <- function(repo_type, scope_type, level_type, y_limit) {
  
  df = giniData
  
  breaks <- seq(0, 1, by=0.05)
  df$bins = cut(df$gini.index, 
                breaks=breaks, 
                include.lowest=TRUE)
  
  data = subset(df, scope.type == scope_type & repository.type == repo_type & scope.log.level.type == level_type)
  
  total_without_logs = nrow(subset(data, scope.log.level.count == 0))
  data = subset(data, scope.log.level.count != 0) # Remove all repos without level logs
  total_logs = sum(data$scope.log.level.count)
  total_repos = nrow(data)
  
  # Heatmap colours
  colour_low = "#002540"
  colour_high = "#78c7ff"
  if (repo_type == "ds") {
    colour_low = "#5c0000"
    colour_high = "#ff7878"
  }

  # Display text
  display_title = sprintf("%s: %s Log Count VS Gini Index", toupper(repo_type), firstup(tolower(level_type)))
  display_label_y = sprintf("%s Logs", firstup(tolower(level_type)))
  display_label_info = sprintf("Total repos with logs: %s \nTotal log count: %s \nTotal repos without logs: %s", total_repos, total_logs, total_without_logs)
  
  breaks <- 10^(-10:10)
  minor_breaks <- rep(1:9, 21)*(10^rep(-10:10, each=9))
  
  plot_path = sprintf("./plots/log_levels/%s_level_%s_count.png", repo_type, tolower(level_type))
  png(plot_path)
  # Heatmap 
  p = ggplot(data, aes(x=bins, y=scope.log.level.count)) +
    geom_bin2d(binwidth = 0.10) +
    scale_x_discrete(drop=FALSE) +
    scale_y_log10(breaks = breaks, minor_breaks = minor_breaks, labels = prettyNum, limits = c(1,y_limit)) +
    annotation_logticks(sides = "l") +

    scale_fill_gradient(low=colour_low, high=colour_high) +
  
    theme_bw() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 25),
      axis.title = element_text(size = 20),
      axis.text = element_text(size = 16),
      axis.text.x = element_text(angle = 55, hjust=1),
      legend.title = element_text(size = 20),
      legend.text = element_text(size = 12)
    ) +

    xlab("Gini Index") +
    ylab(display_label_y) +
    ggtitle(display_title) +
    labs(fill = "Repository Count" ) +

    stat_bin2d(geom = "text", aes(label = ..count..), binwidth = 0.10, col="white", size= 12/.pt) +

    geom_label(
      label=display_label_info,
      x=0.5, y=Inf,
      vjust = "inward", hjust = "inward",
      label.padding = unit(0.35, "lines"),
      label.size = 0.20,
      color = "black",
      fill = alpha(c("white"),0.15),
      size= 15/.pt
    )
  
  ggsave(plot_path, width=20, height=10, units = "in", dpi = 300)
}