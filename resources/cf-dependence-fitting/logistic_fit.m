%%
clear all; close all; 
cfs = [300;400;500;600;700;900;1000;1500;2000;3000;4000;5000;6000;7000;8000;9000;10000;15000;];
percentages = [21;21;26;20;26;30;25;26;28;30;44;40;43;42;41;40;44;43;];

K=22;
r=.0009;
t0=2500;
tt=0:15000;
figure(1);semilogx(cfs,percentages,'o',tt,logistic_func(tt,K,r,t0));
title('First test')
xlabel('center frequency')
ylabel('percent low spont')

%% optimize
num_r=100;
rvec=linspace(.0009,.0025,num_r);

num_t0=5000;
t0_vec=linspace(2200,4200,num_t0);

penalty_array=zeros(num_t0,num_r);
for i=1:num_t0
    for j=1:num_r
        penalty_array(i,j)=penalty_logistic([rvec(j),t0_vec(i)],cfs,percentages);
    end
end
figure(2)
mesh(rvec,t0_vec,penalty_array)
axis tight
xlabel('r')
ylabel('t_0')
ylabel('Penalty Function')
figure(3)
contour(rvec,t0_vec,penalty_array)
hold on;
% finding the best spot on the contour plot and marking with a star:
[m1,p1]=min(penalty_array);
[m2,p2]=min(m1);
best_r=rvec(p2);
best_t0=t0_vec(p1(p2));
plot(best_r,best_t0,'*')
hold off
mytitle=sprintf('Best guess is r=%4.6f, t_0=%5.1f',best_r,best_t0);
title(mytitle);
xlabel('r')
ylabel('t_0')
colorbar