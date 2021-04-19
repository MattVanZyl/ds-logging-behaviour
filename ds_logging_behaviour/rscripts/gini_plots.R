library("ggplot2")
library("gridExtra")

do_plots(giniData$gini.index.file, "Logs Per File")

do_plots(giniData$gini.index.module, "Logs Per Module")
do_plots(giniData$gini.index.function, "Logs Per Function")
do_plots(giniData$gini.index.class, "Logs Per Class")
do_plots(giniData$gini.index.method, "Logs Per Method")


#===============================================================================

do_plots <- function(gini, title) {
  binLabels = seq(0, 1, by=0.1)
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
  d <- ggplot(data = giniData, aes(x = gini, fill = as.factor(repository.type))) 
  d <- d + geom_density(alpha=0.25)
  d <- d + theme(plot.title = element_text(hjust = 0.5))
  d <- d + labs(fill = "Repository Type" )
  d <- d + ylab("Density")
  d <- d + xlab("Gini Index")
  
  m <- grid.arrange(p,d)
  m
}

#===============================================================================

