#new_analysis.r

require(ggplot2)
require(pscl)
require(boot)
require(MASS)

#Zero-inflated Negative Binomial Regression
#http://www.ats.ucla.edu/stat/r/dae/zinbreg.htm

m1 <- zeroinfl(count ~ child + camper | persons,
  data = zinb, dist = "negbin", EM = TRUE)
summary(m1)

#logit model - excess zeros?
