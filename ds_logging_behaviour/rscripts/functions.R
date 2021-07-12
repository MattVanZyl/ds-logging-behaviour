library("ggplot2")
library("gridExtra")
library("dplyr")
library("scales")

source("functions_common.R")

#===============================================================================
plot_categorised_sample <- function(sample){
  
  # Get subsets of data with and without annotations
  df = subset(sample, taxonomy!="#N/A")
  df2 = subset(sample, taxonomy=="#N/A")
  
  total = nrow(sample)
  na_counts = nrow(df2)
  repository_counts = count(df, repository.type)
  
  display_title = sprintf("Categorised Logs Sample (%s)", total)
  display_label_info = sprintf("Total: %s \nDS: %s \nNon-DS: %s \nInconclusive: %s", total, repository_counts[1,2], repository_counts[2,2], na_counts) 
  
  # Colours
  colour_ds = "#cf5d5d"
  colour_nonds = "#65a7d6"
  
  plot_path = sprintf("./plots/categorised_sample_%s.png", total)
  png(plot_path)
  
  p <- ggplot(data = df, aes(x = taxonomy, fill = as.factor(repository.type))) + 
    geom_bar(position = 'dodge') +
    xlab("Category") +
    ylab("Count") +
    labs(fill = "Repository Type" ) +
    ggtitle(display_title) +
    
    geom_label(
      label=display_label_info, 
      x=-Inf, y=Inf,
      vjust = "inward", hjust = "inward",
      label.padding = unit(0.35, "lines"), 
      label.size = 0.20,
      color = "black",
      fill = alpha(c("white"),0.15),
      size= 15/.pt
    ) +
    scale_fill_manual(values = c(colour_ds, colour_nonds)) +
    theme_bw() + 
    theme(
      plot.title = element_text(hjust = 0.5, size = 25),
      axis.title = element_text(size = 20),
      axis.text = element_text(size = 16),
      axis.text.x = element_text(angle = 55, hjust=1),
      legend.title = element_text(size = 20),
      legend.text = element_text(size = 12)
    ) +
    geom_text(
      stat='count', 
      aes(label=..count..), 
      vjust=-0.25, 
      position=position_dodge(width=0.9),
      size= 15/.pt
      )
  
  ggsave(plot_path, width=20, height=10, units = "in", dpi = 300)
}

#===============================================================================
plot_log_distribution <- function(scope_type) {
  data = giniData
  data = subset(data, scope.type == scope_type & scope.log.level.type == "Print") # Select the print level as the data we need is in all the level rows
  
  breaks <- seq(0, 1, by=0.05)
  data$bins = cut(data$gini.index, 
                      breaks=breaks, 
                      include.lowest=TRUE)
  
  # data = subset(data.percent, scope.type == scope_type)
  
  ds_total = nrow(subset(data, repository.type == "ds"))
  nonds_total = nrow(subset(data, repository.type == "non-ds"))
  ds_total_without_logs = nrow(subset(data, scope.log.count == 0 & repository.type == "ds"))
  nonds_total_without_logs = nrow(subset(data, scope.log.count == 0 & repository.type == "non-ds"))
  data = subset(data, scope.log.count != 0) # Remove all repos without scope logs
  ds_total_logs = sum(subset(data, repository.type == "ds")$scope.log.count)
  nonds_total_logs = sum(subset(data, repository.type == "non-ds")$scope.log.count)
  ds_total_with_logs = nrow(subset(data, repository.type == "ds"))
  nonds_total_with_logs = nrow(subset(data, repository.type == "non-ds"))
  
  data.percent = data %>% group_by(repository.type, scope.type, bins) %>%
    summarise(count=n()) %>%
    mutate(percent=count/sum(count))
  
  # Display text
  display_title = sprintf("Log Distribution (%s)", firstup(scope_type))
  display_label_info = sprintf("Total repos: DS = %s Non-DS = %s
Total repos with logs: DS = %s Non-DS = %s
Total log count: DS = %s Non-DS = %s 
Total repos without logs: DS = %s Non-DS = %s", 
                               ds_total, nonds_total,
                               ds_total_with_logs, nonds_total_with_logs, 
                               ds_total_logs, nonds_total_logs, 
                               ds_total_without_logs, nonds_total_without_logs
                               )
  
  # Colours
  colour_ds = "#cf5d5d"
  colour_nonds = "#65a7d6"
  
  plot_path = sprintf("./plots/%s/log_distribution_%s.png", scope_type, scope_type)
  png(plot_path)
  
  # Percentage Plot
  p <- ggplot(data.percent, aes(x = bins, y = percent, fill = as.factor(repository.type), width=.75)) +
    geom_bar(stat="identity", position = 'dodge') +
    scale_y_continuous(labels=percent) + 
    scale_x_discrete(drop=FALSE) +
    scale_fill_manual(values = c(colour_ds, colour_nonds)) +

    xlab("Gini Index") +
    ylab("Percentage of Repositories") +
    labs(fill = "Repository Type" ) +
      
    geom_text(aes(label=paste0(round(percent*100,1),"%"),
                             y=percent+0.0035), size=11/.pt, position=position_dodge(width=1.2)) +
    ggtitle(display_title) +

    theme_bw() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 25),
      axis.title = element_text(size = 20),
      axis.text = element_text(size = 16),
      axis.text.x = element_text(angle = 55, hjust=1),
      legend.title = element_text(size = 20),
      legend.text = element_text(size = 12)
    ) +
    
    geom_label(
      label=display_label_info,
      x=2, y=Inf,
      vjust = "inward", hjust = "inward",
      label.padding = unit(0.35, "lines"),
      label.size = 0.20,
      color = "black",
      fill = alpha(c("white"),0.15),
      size= 15/.pt
    )
  
  ggsave(plot_path, width=20, height=10, units = "in", dpi = 300)
}
#===============================================================================
plot_log_density <- function(scope_type) {
  data = giniData
  
  # Colours
  colour_ds = "#cf5d5d"
  colour_nonds = "#65a7d6"
  
  data = subset(data, scope.type == scope_type & scope.log.count != 0) # Remove all repos without scope logs
  write.csv(data,"test.csv", row.names = FALSE)
  
  display_title = sprintf("Log Density (%s)", firstup(scope_type))
  
  plot_path = sprintf("./plots/%s/log_density_%s.png", scope_type, scope_type)
  png(plot_path)
  
  # Density Plot
  d <- ggplot(data, aes(x = gini.index, fill = as.factor(repository.type))) +
    geom_density(alpha=0.25) +
    scale_fill_manual(values = c(colour_ds, colour_nonds)) +
    theme(plot.title = element_text(hjust = 0.5)) +
    labs(fill = "Repository Type" ) +
    ylab("Density") +
    xlab("Gini Index")+
    ggtitle(display_title) +
    
    theme_bw() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 25),
      axis.title = element_text(size = 20),
      axis.text = element_text(size = 16),
      legend.title = element_text(size = 20),
      legend.text = element_text(size = 12)
    )
  
  ggsave(plot_path, width=20, height=10, units = "in", dpi = 300)
}
