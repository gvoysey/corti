function y = logistic_func(t,K,r,t0)
y=21 + K./(1+exp(-r*(t-t0)));