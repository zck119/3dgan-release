require 'nn'
require 'xlua'
assert(pcall(function () mat = require('fb.mattorch') end) or pcall(function() mat = require('matio') end), 'no mat IO interface available')


cmd = torch.CmdLine()
cmd:option('-gpu', 0, 'GPU id, starting from 1. Set it to 0 to run it in CPU mode. ')
cmd:option('-class', 'chair', 'class to run forward with. Use all to run all 5 classes')
cmd:option('-sample', false, 'whether to sample input latent vectors from an i.i.d. uniform distribution, or to generate shapes with demo vectors')
cmd:option('-bs', 100, 'batch size')
cmd:option('-ss', 100, 'number of generated shapes, only used in `-sample` mode')

opt = cmd:parse(arg or {})
if opt.gpu > 0 then 
    require 'cunn'
    require 'cudnn'
    require 'cutorch'
    cutorch.setDevice(opt.gpu)
end
all_classes = {'car', 'chair', 'desk', 'gun', 'sofa'}
class_used = {}
for _,c in ipairs(all_classes) do 
    if c == opt.class or opt.class == 'all' then
        class_used[#class_used+1] = c
    end
end
assert(#class_used > 0, 'Invalid class name: '..opt.class)
-------------------------------------------------------------------------------
for _,class in ipairs(class_used) do 
    print("=====================================================")
    print("==> Running with class: "..class)
    print("==> Loading network")
    if opt.gpu == 0 then 
        netG = torch.load('./models_cpu/'..class..'_G_cpu.t7')
    else
        netG = torch.load('./models_gpu/'..class..'_G_gpu.t7')
    end 
    nz = netG:get(1).nInputPlane    -- latent vector dimensions
    netG:apply(function(m) if torch.type(m):find('Convolution') then m.bias:zero() end end)     -- convolution bias is removed during training
    netG:evaluate()

    print("==> Setting inputs")
    if not opt.sample then 
        inputs = mat.load('./demo_inputs/'..class..'.mat')['inputs']:double()
    else 
        inputs = torch.rand(opt.ss, nz)
    end
    num_points = inputs:size(1)
    inputs = inputs:reshape(num_points, nz, 1, 1, 1) -- since matlab does not support singleton dimension. Reshape will fail if dimension does not match nz. 
    all_res = torch.zeros(num_points, 1, 64, 64, 64):double()

    input = torch.zeros(opt.bs, nz, 1, 1, 1)

    if opt.gpu > 0 then 
        netG = netG:cuda()
        netG = cudnn.convert(netG, cudnn)
        input = input:cuda()
    end

    print("==> Forward propagation")
    for i = 1, math.ceil(num_points / opt.bs) do
        ind_low = (i-1) * opt.bs + 1
        ind_high = math.min(i * opt.bs, num_points)
        input:zero()
        input[{{1, ind_high-ind_low+1},{},{},{},{}}] = inputs[{{ind_low, ind_high},{},{},{},{}}]
        res = netG:forward(input):double()
        all_res[{{ind_low, ind_high},{},{},{},{}}] = res[{{1, ind_high-ind_low+1},{},{},{},{}}]
    end

    print("==> Saving result")
    os.execute('mkdir -p ./output')
    if opt.sample then 
        savename = class..'_sample.mat' 
    else 
        savename = class..'_demo.mat'
    end
    savename = sys.concat('./output', savename)
    mat.save(savename, {['inputs'] = inputs, ['voxels'] = all_res})

    print("==> Saving done")
end

