source("functions_common.R")

plot_scope_count <- function(repo_type, scope_type) {
  
  df = giniData
  
  breaks <- seq(0, 1, by=0.05)
  df$bins = cut(df$gini.index, 
                breaks=breaks, 
                include.lowest=TRUE)
  
  data = subset(df, scope.type == scope_type & repository.type == repo_type)
  
  breaks <- 10^(-10:10)
  minor_breaks <- rep(1:9, 21)*(10^rep(-10:10, each=9))

  write.csv(data,"test.csv", row.names = FALSE)
  
  # Heatmap colours
  colour_low = "#002540"
  colour_high = "#78c7ff"
  if (repo_type == "ds") {
    colour_low = "#5c0000"
    colour_high = "#ff7878"
  }
  
  # Get subsets of data
  gini_zero = nrow(subset(data, gini.index == 0))
  no_logs = nrow(subset(data, gini.index == 0 & scope.log.count == 0))
  all_logs_in_one = nrow(subset(data, gini.index == 0 & scope.log.count != 0))
  gini_one = nrow(subset(data, gini.index == 1))
  
  data = subset(data, scope.log.count != 0)
  
  # Display text
  display_title = sprintf("%s: %s count VS gini index", toupper(repo_type), firstup(scope_type))
  display_label_y = sprintf("%s Count", firstup(scope_type))
  display_label_info = sprintf("Repos with gini index of zero: %s \n    Repos with no logs: %s \n    Repos with logs evenly distributed: %s \n\nRepos with gini index of one: %s", gini_zero, no_logs, all_logs_in_one, gini_one) 
  
  plot_path = sprintf("./plots/%s/%s_scopecount_vs_gini_%s.png", scope_type, repo_type, scope_type)
  png(plot_path)
  # Heatmap 
  p = ggplot(data, aes(x=bins, y=scope.count)) +
    geom_bin2d(binwidth = 0.10) +
    scale_x_discrete(drop=FALSE) +
    scale_y_log10(breaks = breaks, minor_breaks = minor_breaks, labels = prettyNum) +
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
   
    stat_bin2d(geom = "text", aes(label = ..count..), binwidth = 0.10, col="white", size= 3) +
    
    geom_label(
      label=display_label_info, 
      x=2, y=Inf,
      vjust = "inward", hjust = "inward",
      label.padding = unit(0.35, "lines"), 
      label.size = 0.20,
      color = "black",
      fill = alpha(c("white"),0.15)
      ) 
  ggsave(plot_path, width=20, height=10, units = "in", dpi = 300)
}
# ==============================================================================
plot_loc <- function(repo_type, scope_type) {
  
  df = giniData
  
  breaks <- seq(0, 1, by=0.05)
  df$bins = cut(df$gini.index, 
                breaks=breaks, 
                include.lowest=TRUE)
  
  data = subset(df, scope.type == scope_type & repository.type == repo_type)
  
  breaks <- 10^(-10:10)
  minor_breaks <- rep(1:9, 21)*(10^rep(-10:10, each=9))
  
  # Heatmap colours
  colour_low = "#002540"
  colour_high = "#78c7ff"
  if (repo_type == "ds") {
    colour_low = "#5c0000"
    colour_high = "#ff7878"
  }
  
  # Display text
  display_title = sprintf("%s: Lines of Code VS gini index", toupper(repo_type))
  
  # Heatmap 
  p = ggplot(data, aes(x=bins, y=repository.lines.of.code)) +
    geom_bin2d(binwidth = 0.10) +
    scale_x_discrete(drop=FALSE) +
    scale_y_log10(breaks = breaks, minor_breaks = minor_breaks, labels = prettyNum) +
    annotation_logticks(sides = "l") +
    
    scale_fill_gradient(low=colour_low, high=colour_high) +
    
    theme_bw() + 
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(axis.text.x = element_text(angle = 55, hjust=1)) +
    
    xlab("Gini Index") +
    ylab("Lines of Code") +
    ggtitle(display_title) +
    labs(fill = "Repository Count" ) +
    
    stat_bin2d(geom = "text", aes(label = ..count..), binwidth = 0.10, col="white", size= 3)
    
  p
}

# ==============================================================================
plot_log_count <- function(repo_type, scope_type) {
  
  df = giniData
  
  breaks <- seq(0, 1, by=0.05)
  df$bins = cut(df$gini.index, 
                breaks=breaks, 
                include.lowest=TRUE)
  
  
  data = subset(df, scope.type == scope_type & repository.type == repo_type)
  
  breaks <- 10^(-10:10)
  minor_breaks <- rep(1:9, 21)*(10^rep(-10:10, each=9))
  
  # Heatmap colours
  colour_low = "#002540"
  colour_high = "#78c7ff"
  if (repo_type == "ds") {
    colour_low = "#5c0000"
    colour_high = "#ff7878"
  }
  
  # Display text
  display_title = sprintf("%s: Number of logs VS gini index", toupper(repo_type))
  
  # Heatmap 
  p = ggplot(data, aes(x=bins, y=scope.log.count)) +
    geom_bin2d(binwidth = 0.10) +
    scale_x_discrete(drop=FALSE) +
    scale_y_log10(breaks = breaks, minor_breaks = minor_breaks, labels = prettyNum) +
    annotation_logticks(sides = "l") +
    
    scale_fill_gradient(low=colour_low, high=colour_high) +
    
    theme_bw() + 
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(axis.text.x = element_text(angle = 55, hjust=1)) +
    
    xlab("Gini Index") +
    ylab("Log Count") +
    ggtitle(display_title) +
    labs(fill = "Repository Count" ) +
    
    stat_bin2d(geom = "text", aes(label = ..count..), binwidth = 0.10, col="white", size= 3)
  
  p
}