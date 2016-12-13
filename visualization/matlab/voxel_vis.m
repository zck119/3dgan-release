function voxel_vis(i,d,c,alpha);

%VOXEL function to draw a 3-D voxel in a 3-D plot
%
%Usage
%   voxel(start,size,color,alpha);
%
%   will draw a voxel at 'start' of size 'size' of color 'color' and
%   transparency alpha (1 for opaque, 0 for transparent)
%   Default size is 1
%   Default color is blue
%   Default alpha value is 1
%
%   start is a three element vector [x,y,z]
%   size the a three element vector [dx,dy,dz]
%   color is a character string to specify color 
%       (type 'help plot' to see list of valid colors)
%   
%
%   voxel_vis([2 3 4],[1 2 3],'r',0.7);
%   axis([0 10 0 10 0 10]);
%

%   Suresh Joel Apr 15,2003
%           Updated Feb 25, 2004

switch(nargin),
case 0
    disp('Too few arguements for voxel');
    return;
case 1
    l=1;    %default length of side of voxel is 1
    c='b';  %default color of voxel is blue
case 2,
    c='b';
case 3,
    alpha=1;
case 4,
    %do nothing
otherwise
    disp('Too many arguements for voxel');
end;

x=[i(1)+[0 0 0 0 d(1) d(1) d(1) d(1)]; ...
        i(2)+[0 0 d(2) d(2) 0 0 d(2) d(2)]; ...
        i(3)+[0 d(3) 0 d(3) 0 d(3) 0 d(3)]]';
for n=1:3,
    if n==3,
        x=sortrows(x,[n,1]);
    else
        x=sortrows(x,[n n+1]);
    end;
    temp=x(3,:);
    x(3,:)=x(4,:);
    x(4,:)=temp;
    h=patch(x(1:4,1),x(1:4,2),x(1:4,3),c);
    set(h,'FaceAlpha',alpha);
    temp=x(7,:);
    x(7,:)=x(8,:);
    x(8,:)=temp;
    %h=patch(x(5:8,1),x(5:8,2),x(5:8,3),c, 'EdgeColor','none');
    h=patch(x(5:8,1),x(5:8,2),x(5:8,3),c);
    set(h,'FaceAlpha',alpha);
end;
