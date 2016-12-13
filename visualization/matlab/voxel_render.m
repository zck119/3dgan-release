function fig = voxel_render(voxel, step, threshold, visibility)
% generate figure handle using input voxel matrix, threshold and a colormap. 
% The input matrix 'voxel' must be 3-dimensional
% 'step' is used for downsampling to reduce computation burden. step should be 1,2, or 4

assert(ndims(voxel) == 3);

cmap_size = 1000;
cmap = jet(cmap_size);

% pooling
voxel = pooling(voxel, step, 'max');

% Add sigmoid to get better plots! 
voxel = sigmf(voxel, [10 0.5]); 

if visibility 
  fig = figure('Renderer', 'painters');
else
  fig = figure('Visible', 'off', 'Renderer', 'painters');
end

% used for find axis range
minx = size(voxel, 3);
miny = size(voxel, 2);
minz = size(voxel, 1);
maxx = 0;
maxy = 0;
maxz = 0;  

for i = 1 : size(voxel, 1)
  for j = 1 : size(voxel, 2)
    for k = 1 : size(voxel, 3)
      length = voxel(i, j, k);
      if length > threshold
        color = cmap(max(1, ceil(length * cmap_size)), :);
        voxel_vis([i+0.5-length*0.5, j+0.5-length*0.5, k+0.5-length*0.5], [length, length, length], color, length);
        
        minx = min(i, minx);
        miny = min(j, miny);
        minz = min(k, minz);
        maxx = max(i, maxx);
        maxy = max(j, maxy);
        maxz = max(k, maxz);
      end
    end
  end
end

% max has to be larger than mean 
maxx = max(minx+1, maxx);
maxy = max(miny+1, maxy);
maxz = max(minz+1, maxz);

axisrange = [minx maxx miny maxy minz maxz];
axis(axisrange);
axis equal;

angle = pi/pi*180;
[az, e1] = view;
view(az + angle, e1);

end
