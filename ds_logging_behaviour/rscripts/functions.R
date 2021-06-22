library("ggplot2")
library("gridExtra")
library("dplyr")
library("scales")

source("functions_common.R")

#===============================================================================

# do_plots <- function(gini, title) {
#   binLabels = seq(0, 1, by=0.5)
#   giniData$bins = cut(gini, breaks = binLabels, include.lowest = TRUE)
#   
#   # Percentage Plot
#   p <- ggplot(data = giniData, aes(x = as.factor(bins), fill = as.factor(repository.type))) + 
#     geom_bar(aes(y = (..count..)/sum(..count..)), position="dodge", alpha=0.5) +
#     scale_y_continuous(labels = scales::percent) + 
#     scale_x_discrete(drop=FALSE) +
#     ggtitle(title) + 
#     theme(plot.title = element_text(hjust = 0.5)) + 
#     labs(fill = "Repository Type" ) + 
#     ylab("Percentage of Repositories") + 
#     xlab("Gini Index")
#   
#   # Density Plot
#   d <- ggplot(data = giniData, aes(x = gini, fill = as.factor(repository.type))) + 
#     geom_density(alpha=0.25) + 
#     theme(plot.title = element_text(hjust = 0.5)) + 
#     labs(fill = "Repository Type" ) + ylab("Density") + 
#     xlab("Gini Index")
#   
#   m <- grid.arrange(p,d)
#   m
# }

#===============================================================================
plot_annotated <- function(sample){
  
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
  
  p <- ggplot(data = df, aes(x = taxonomy, fill = as.factor(repository.type))) + 
    geom_bar(position = 'dodge') +
    xlab("Category") +
    ylab("Count") +
    ggtitle(display_title) +
    
    geom_label(
      label=display_label_info, 
      x=-Inf, y=Inf,
      vjust = "inward", hjust = "inward",
      label.padding = unit(0.35, "lines"), 
      label.size = 0.20,
      color = "black",
      fill = alpha(c("white"),0.15)
    ) +
    
    scale_fill_manual(values = c(colour_ds, colour_nonds)) +
    theme_bw() + 
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(axis.text.x = element_text(angle = 55, hjust=1)) +
    labs(fill = "Repository Type" ) +
    
    geom_text(stat='count', aes(label=..count..), vjust=-0.25, position=position_dodge(width=0.9))
  
  p
}

#===============================================================================
# plot_scope <- function(type, title) {
#   
#   breaks <- seq(0, 1, by=0.05)
#   giniData$bins = cut(giniData$gini.index, 
#                       breaks=breaks, 
#                       include.lowest=TRUE)
# 
#   giniData.percent = giniData %>% group_by(repository.type, scope.type, bins) %>%
#     summarise(count=n()) %>%
#     mutate(percent=count/sum(count))
#   
#   test = subset(giniData.percent, scope.type == type)
#   
#   test2 = subset(giniData, scope.type == type)
#   repository_counts = count(test2, repository.type)
#   print(repository_counts, row.names=FALSE)
#   
#   # Percentage Plot
#   p <- ggplot(data = test, aes(x = bins, y = percent, fill = as.factor(repository.type), width=.75)) +
#     geom_bar(stat="identity", position = 'dodge') +
#     # facet_grid(. ~ scope.type) +
#     scale_x_discrete(drop=FALSE) +
#     xlab("Gini Index") +
#     scale_y_continuous(labels=percent) + #, limits=c(0,0.27)) +
#     ylab("Percentage of Repositories") +
#     labs(fill = "Repository Type" ) +
#     geom_text(data=test, aes(label=paste0(round(percent*100,1),"%"),
#                                          y=percent+0.0035), size=1.85, position=position_dodge(width=1.2)) +
#     ggtitle(title) +
#     theme(plot.title = element_text(hjust = 0.5)) +
#     theme(axis.text.x = element_text(angle = 55, hjust=1))  
#     
#     # geom_label(
#     #   label=sprintf("ds: %s", repository_counts[1,2]),
#     #   x=2,y=max(percent)-0.0035,
#     #   label.padding = unit(0.55, "lines"),
#     #   label.size = 0.35,
#     #   color = "black",fill=NA) +
#     # 
#     # geom_label(
#     #   label=sprintf("non-ds: %s", repository_counts[2,2]),
#     #   x=-1,y=max(percent)-0.0035,
#     #   label.padding = unit(0.55, "lines"),
#     #   label.size = 0.35,
#     #   color = "black",fill=NA)
#   
#   p
#   
# }
#===============================================================================
plot_log_distribution <- function(scope_type) {
  df = giniData
  
  breaks <- seq(0, 1, by=0.05)
  df$bins = cut(df$gini.index, 
                      breaks=breaks, 
                      include.lowest=TRUE)
  
  df.percent = df %>% group_by(repository.type, scope.type, bins) %>%
    summarise(count=n()) %>%
    mutate(percent=count/sum(count))
  
  data = subset(df.percent, scope.type == scope_type)
  
  # test2 = subset(giniData, scope.type == type)
  # repository_counts = count(test2, repository.type)
  # print(repository_counts, row.names=FALSE)
  
  # Display text
  display_title = "Log Distribution"
  
  # Colours
  colour_ds = "#cf5d5d"
  colour_nonds = "#65a7d6"
  
  # Percentage Plot
  p <- ggplot(data, aes(x = bins, y = percent, fill = as.factor(repository.type), width=.75)) +
    geom_bar(stat="identity", position = 'dodge') +
    scale_y_continuous(labels=percent) + #, limits=c(0,0.27)) +
    scale_x_discrete(drop=FALSE) +
    scale_fill_manual(values = c(colour_ds, colour_nonds)) +
 
    xlab("Gini Index") +
    ylab("Percentage of Repositories") +
    labs(fill = "Repository Type" ) +
      
    geom_text(aes(label=paste0(round(percent*100,1),"%"),
                             y=percent+0.0035), size=1.85, position=position_dodge(width=1.2)) +
    ggtitle(display_title) +

    theme_bw() + 
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(axis.text.x = element_text(angle = 55, hjust=1))  
  
  p
}

plot_log_density <- function(scope_type) {
  df = giniData
  
  # Colours
  colour_ds = "#cf5d5d"
  colour_nonds = "#65a7d6"
  
  data = subset(df, scope.type == scope_type)
  display_title = "Log Density"
  
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
    theme(plot.title = element_text(hjust = 0.5))
  
  d
}
