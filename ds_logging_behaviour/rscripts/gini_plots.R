library("ggplot2")
library("gridExtra")
library("dplyr")
library("scales")

#plot_annotated(logSample)
#plot_annotated(logSample2)
plot_scope("file", "Logs Per File") 
plot_scope("class", "Logs Per Class") 
plot_scope("function", "Logs Per Function")
plot_scope("method", "Logs Per Method")
plot_scope("module", "Logs Per Module")

# do_plots(giniData$gini.index.file, "Logs Per File")
# 
# do_plots(giniData$gini.index.module, "Logs Per Module")
# do_plots(giniData$gini.index.function, "Logs Per Function")
# do_plots(giniData$gini.index.class, "Logs Per Class")
# do_plots(giniData$gini.index.method, "Logs Per Method")


#===============================================================================

do_plots <- function(gini, title) {
  binLabels = seq(0, 1, by=0.5)
  giniData$bins = cut(gini, breaks = binLabels, include.lowest = TRUE)
  
  # Percentage Plot
  p <- ggplot(data = giniData, aes(x = as.factor(bins), fill = as.factor(repository.type))) + 
    geom_bar(aes(y = (..count..)/sum(..count..)), position="dodge", alpha=0.5) +
    scale_y_continuous(labels = scales::percent) + 
    scale_x_discrete(drop=FALSE) +
    ggtitle(title) + 
    theme(plot.title = element_text(hjust = 0.5)) + 
    labs(fill = "Repository Type" ) + 
    ylab("Percentage of Repositories") + 
    xlab("Gini Index")
  
  # Density Plot
  d <- ggplot(data = giniData, aes(x = gini, fill = as.factor(repository.type))) + 
    geom_density(alpha=0.25) + 
    theme(plot.title = element_text(hjust = 0.5)) + 
    labs(fill = "Repository Type" ) + ylab("Density") + 
    xlab("Gini Index")
  
  m <- grid.arrange(p,d)
  m
}

#===============================================================================
plot_annotated <- function(sample){

  # Get subsets of data with and without annotations
  df = subset(sample, final.annotation!="#N/A")
  df2 = subset(sample, final.annotation=="#N/A")
  
  na_counts = nrow(df2)
  repository_counts = count(df, repository.type)
  
  p <- ggplot(data = df, aes(x = final.annotation, fill = as.factor(repository.type))) + 
    geom_bar(position = 'dodge') +
    theme(axis.text.x = element_text(angle = 55, hjust=1)) + 
    xlab("category") +
    
    geom_label(
      label=sprintf("ds: %s", repository_counts[1,2]), 
      x=-Inf, y=Inf,
      hjust=-0.22, vjust=1.2,
    # x=0.85,y=28,
      label.padding = unit(0.55, "lines"), # Rectangle size around label
      label.size = 0.35,
      color = "black",fill=NA) + 
    
    geom_label(
      label=sprintf("non-ds: %s", repository_counts[2,2]), 
      x=-Inf, y=Inf,
      hjust=-0.15, vjust=2.4,
      label.padding = unit(0.55, "lines"), # Rectangle size around label
      label.size = 0.35,
      color = "black",fill=NA) +
    
    geom_label(
      label=sprintf("inconclusive: %s", na_counts), 
      x=-Inf, y=Inf,
      hjust=-0.11, vjust=3.6,
      label.padding = unit(0.55, "lines"), # Rectangle size around label
      label.size = 0.35,
      color = "black",fill=NA) +
    
    labs(fill = "Repository Type" ) +
    
    geom_text(stat='count', aes(label=..count..), vjust=-0.25, position=position_dodge(width=0.9))
  
  p
}

#===============================================================================
plot_scope <- function(type, title) {
  
  breaks <- seq(0, 1, by=0.05)
  giniData$bins = cut(giniData$gini.index, 
                      breaks=breaks, 
                      include.lowest=TRUE)

  giniData.percent = giniData %>% group_by(repository.type, scope.type, bins) %>%
    summarise(count=n()) %>%
    mutate(percent=count/sum(count))
  
  test = subset(giniData.percent, scope.type == type)
  
  test2 = subset(giniData, scope.type == type)
  repository_counts = count(test2, repository.type)
  print(repository_counts, row.names=FALSE)
  
  # Percentage Plot
  p <- ggplot(data = test, aes(x = bins, y = percent, fill = as.factor(repository.type), width=.75)) +
    geom_bar(stat="identity", position = 'dodge') +
    # facet_grid(. ~ scope.type) +
    scale_x_discrete(drop=FALSE) +
    xlab("Gini Index") +
    scale_y_continuous(labels=percent) + #, limits=c(0,0.27)) +
    ylab("Percentage of Repositories") +
    labs(fill = "Repository Type" ) +
    geom_text(data=test, aes(label=paste0(round(percent*100,1),"%"),
                                         y=percent+0.0035), size=1.85, position=position_dodge(width=1.2)) +
    ggtitle(title) +
    theme(plot.title = element_text(hjust = 0.5)) +
    theme(axis.text.x = element_text(angle = 55, hjust=1))  
    
    # geom_label(
    #   label=sprintf("ds: %s", repository_counts[1,2]),
    #   x=2,y=max(percent)-0.0035,
    #   label.padding = unit(0.55, "lines"),
    #   label.size = 0.35,
    #   color = "black",fill=NA) +
    # 
    # geom_label(
    #   label=sprintf("non-ds: %s", repository_counts[2,2]),
    #   x=-1,y=max(percent)-0.0035,
    #   label.padding = unit(0.55, "lines"),
    #   label.size = 0.35,
    #   color = "black",fill=NA)
  
  p
  
}

