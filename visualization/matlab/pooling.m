function voxel = pooling(voxel_original, step, method)
  if strcmp(method, 'mean')
	  % mean pooling:
	  voxel = squeeze(mean(reshape(voxel_original, step, size(voxel_original, 1) / step, size(voxel_original, 2), size(voxel_original, 3)), 1));
	  voxel = squeeze(mean(reshape(voxel, size(voxel, 1), step, size(voxel, 2) / step, size(voxel, 3)), 2));
	  voxel = squeeze(mean(reshape(voxel, size(voxel, 1), size(voxel, 2), step, size(voxel, 3) / step), 3));
  elseif strcmp(method, 'max')
	  %% max pooling:
	  voxel = squeeze(max(reshape(voxel_original, step, size(voxel_original, 1) / step, size(voxel_original, 2), size(voxel_original, 3)), [], 1));
	  voxel = squeeze(max(reshape(voxel, size(voxel, 1), step, size(voxel, 2) / step, size(voxel, 3)), [], 2));
	  voxel = squeeze(max(reshape(voxel, size(voxel, 1), size(voxel, 2), step, size(voxel, 3) / step), [], 3));
  else 
  	error('Unsupported pooling method. Only mean and max are supported')
  end
end