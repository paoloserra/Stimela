import os
import sys
import logging
import Crasa.Crasa as crasa
import astropy.io.fits as pyfits

sys.path.append("/scratch/stimela")

utils = __import__('utils')

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value

noise_image = args.pop('noise_image', False)
if noise_image:
    noise_sigma = args.pop('noise_sigma')
    noise_hdu = pyfits.open(noise_image)
    noise_data = noise_hdu[0].data
    noise_std = noise_data.std()
    threshold = noise_sigma*noise_std
    args['threshold'] = '{}Jy'.format(threshold)
else:
    args.pop('noise_sigma')


prefix = args['imagename']
port2fits = args.pop('port2fits', True)
keep_casa_images = args.pop("keep_casa_images", False)

task = crasa.CasaTask(cab["binary"], **args)
task.run()

nterms = args.get("nterms", 1)
images = ["flux", "model", "residual", "psf", "image"]
STD_IMAGES = images[:4]

convert = []
if port2fits:
    for image in images:
        img = "{:s}.{:s}".format(prefix, image)
        if image == 'flux':
            _images = [img]
        elif nterms > 1:
            _images = ["%s.tt%d" % (img, d) for d in range(nterms)]
            if image == "image":
                if nterms == 2:
                    alpha = img+".alpha"
                    alpha_err = img+".alpha.error"
                    _images += [alpha, alpha_err]
                if nterms == 3:
                    beta = img+".beta"
                    beta_err = img+".beta.error"
                    _images += [beta, beta_err]
        else:
            _images = [img]
        convert += _images

for _image in convert:
    sys.stdout.write(_image)
    if _image in STD_IMAGES and (not os.path.exists(_image)):
        raise RuntimeError(
            "Standard output from CASA clean task not found. Something went wrong durring cleaning, take a look at the logs and such")

    elif os.path.exists(_image):
        task = crasa.CasaTask(
            "exportfits", **dict(imagename=_image, fitsimage=_image+".fits", overwrite=True))
        task.run()

if not keep_casa_images:
    for _image in convert:
        utils.xrun("rm", ["-rf", _image])
