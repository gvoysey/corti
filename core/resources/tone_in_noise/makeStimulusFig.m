function makeStimulusFig()
files = dir('*.wav');
rows = zeros(length(files),30080);
legend_labels = {};
for i = 1:length(files)
    x = audioread(files(i).name);
    if(length(x) == 15080)
        x = padarray(x, (30080-15080)/2,0,'both');
    end
    rows(i,:) = x;
    name = strsplit(files(i).name,'-');
    if(length(name) > 2)
        temp = name(4);
        legend_labels{i} = [temp{1}(1:2), ' dB SPL'];
    else
        legend_labels{i} = 'Clicks in quiet';
    end
end

figure;
fs = 100e3;
time = linspace(0,30080/fs, 30080);
plot_with_offset(gca(), time,rows, 'Stimuli Used');
xlabel('time, s');
legend(legend_labels);

savefig('stimuli-used.fig');



end


function plot_with_offset(ax, x, data, title_text)
n_rows = size(data,1);
offset = max(max(data)) * 1.75; 
offset_vector = (offset:offset:n_rows*offset)';
data_plus_offset = bsxfun(@plus,data,offset_vector);
plot(ax,x,data_plus_offset');
title(ax,title_text);
end