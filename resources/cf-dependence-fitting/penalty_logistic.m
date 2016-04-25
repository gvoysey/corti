function z=penalty_logistic(params,t,y)
% This is the function e in equation (95) on page 183
r=params(1);t0=params(2);

h=1./(1+exp(-r*(t-t0)));

numerator  =  -dot(h,y)^2;
denominator =  dot(h,h);
z=numerator/denominator;