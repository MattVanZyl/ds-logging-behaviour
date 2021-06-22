# ==============================================================================
plot_levels <- function(repo_type, scope_type, level_type, y_limit) {
  
  df = giniData
  
  breaks <- seq(0, 1, by=0.05)
  df$bins = cut(df$gini.index, 
                breaks=breaks, 
                include.lowest=TRUE)
  
  data = subset(df, scope.type == scope_type & repository.type == repo_type)
  
  # print(data, row.names=FALSE)
  
  # Heatmap colours
  colour_low = "#002540"
  colour_high = "#78c7ff"
  if (repo_type == "ds") {
    colour_low = "#5c0000"
    colour_high = "#ff7878"
  }
  
  log_level_data = data$scope.log.level.print
  if (level_type == "debug") {
    log_level_data = data$scope.log.level.debug
  } else if (level_type == "info") {
    log_level_data = data$scope.log.level.info
  } else if (level_type == "error") {
    log_level_data = data$scope.log.level.error
  } else if (level_type == "critical") {
    log_level_data = data$scope.log.level.critical
  } else if (level_type == "warning") {
    log_level_data = data$scope.log.level.warning
  }
  
  # total = nrow(log_level_data)
  # display_label_info = sprintf("Total: %s", total) 
  
  # Display text
  display_title = sprintf("%s: %s Log Count VS Gini Index", toupper(repo_type), firstup(level_type))
  display_label_y = sprintf("%s Logs", firstup(level_type))
  
  breaks <- 10^(-10:10)
  minor_breaks <- rep(1:9, 21)*(10^rep(-10:10, each=9))
  
  # Heatmap 
  p = ggplot(data, aes(x=bins, y=log_level_data)) +
    geom_bin2d(binwidth = 0.10) +
    scale_x_discrete(drop=FALSE) +
    scale_y_log10(breaks = breaks, minor_breaks = minor_breaks, labels = prettyNum, limits = c(1,y_limit)) +
    annotation_logticks(sides = "l") +

    scale_fill_gradient(low=colour_low, high=colour_high) +
  
    theme_bw() +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(axis.text.x = element_text(angle = 55, hjust=1)) +

    xlab("Gini Index") +
    ylab(display_label_y) +
    ggtitle(display_title) +
    labs(fill = "Repository Count" ) +

    stat_bin2d(geom = "text", aes(label = ..count..), binwidth = 0.10, col="white", size= 3) 

    # geom_label(
    #   label=display_label_info, 
    #   x=2, y=Inf,
    #   vjust = "inward", hjust = "inward",
    #   label.padding = unit(0.35, "lines"), 
    #   label.size = 0.20,
    #   color = "black",
    #   fill = alpha(c("white"),0.15)
    # ) 
  p
  
  # # Colours
  # colour_ds = "#cf5d5d"
  # colour_nonds = "#65a7d6"
  
  # # Density Plot
  # p <- ggplot(data, aes(x = scope.log.level.debug, fill = as.factor(repository.type))) +
  #   geom_density(alpha=0.25) +
  #   scale_fill_manual(values = c(colour_ds, colour_nonds)) +
  #   theme(plot.title = element_text(hjust = 0.5)) +
  #   # labs(fill = "Repository Type" ) +
  #   # ylab("Density") +
  #   # xlab("Gini Index")+
  #   # ggtitle(display_title) +
  #   
  #   theme_bw() + 
  #   theme(plot.title = element_text(hjust = 0.5))
  # p
  # 
  # # Density Plot
  # d <- ggplot(data, aes(x = scope.log.level.print, fill = as.factor(repository.type))) +
  #   geom_density(alpha=0.25) +
  #   scale_fill_manual(values = c(colour_ds, colour_nonds)) +
  #   theme(plot.title = element_text(hjust = 0.5)) +
  #   # labs(fill = "Repository Type" ) +
  #   # ylab("Density") +
  #   # xlab("Gini Index")+
  #   # ggtitle(display_title) +
  #   
  #   theme_bw() + 
  #   theme(plot.title = element_text(hjust = 0.5))
  # d
  # 
  # 
  # m <- grid.arrange(p,d)
  # m
}