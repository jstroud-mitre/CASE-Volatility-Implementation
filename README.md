### Proof-of-Concept CASE Volatility Plugins
This repository contains a sub-set of [Volatility](https://github.com/volatilityfoundation/volatility/)
plugins that produce output in the [CASE/UCO](https://github.com/ucoproject/) format.

These plugins have been taken from core Volatility plugins and adapted
the output to produce CASE/UCO JSON-LD. These currently are **proof-of-concept
only**, and may not fully comply to the CASE/UCOontology as it is an evolving standard.

This repository takes the following plugins from the [Volatility framework](https://github.com/volatilityfoundation/volatility/)
and adapats the output to be CASE/UCO compliant based on the v0.1.0 release:

* [handles.py](https://github.com/volatilityfoundation/volatility/blob/master/volatility/plugins/handles.py)
* [procdump.py](https://github.com/volatilityfoundation/volatility/blob/master/volatility/plugins/procdump.py)
* [cmdline.py](https://github.com/volatilityfoundation/volatility/blob/master/volatility/plugins/cmdline.py)


All [Volatility](https://github.com/volatilityfoundation/volatility/) work belongs to their respective authors which can be found [here](https://github.com/volatilityfoundation/volatility/blob/master/AUTHORS.txt).


### Installation  of 3rd Party Libraries
* [CASE Python Library](https://github.com/ucoProject/CASE-Python-API).
* [Volatility Python library](https://github.com/volatilityfoundation/volatility/wiki/Installation).


### Running Custom PoC Plugins


##### CASE/UCO Handle List from Memory Image
```
vol.py --plugins='volplugs/src/' -f memory_images/memory.img --profile WinXPSP2x86 casehandles
```

##### CASE/UCO Procdump
```
vol.py --plugins='volplugs/src/' -f memory_images/memory.img caseprocdump --dump-dir dumpdir
```

#### CASE/UCO Commandline dumping
```
vol.py --plugins='volplugs/src/' -f memory_images/memory.img casecmdline
```
