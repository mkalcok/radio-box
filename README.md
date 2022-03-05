# radio-box
CLI tool for Internet Radio streaming

## Installation (Ubuntu20.04 + Raspberry Pi)

Targeted platform for this tool is a Raspberry Pi zero running Raspberry Pi OS 
(Bullseye). This brings a lot of complications regarding the dependencies and
making sound actually work. Following steps should setup everything on fresh
installation.

Before starting, make sure that the user that'll be running `radio-box` is in
the `audio` group.
```
sudo usermod -a -G audio <username>
```
This change takes effect only in new sessions, so to be safe, logout and
login again.

Now the dependencies:
```
sudo apt install --no-install-recommends vlc-bin vlc-plugin-base
sudo apt install alsa-base tinyproxy
```

---
**NOTE**

Option `--no-install-recommends` is required on headless system to ensure
that entire desktop environment is not installed by `vlc-plugin-base` package.

---

Verify that `alsa` detects your sound card by running
```
aplay -l
```
and the output should look like this:
```
**** List of PLAYBACK Hardware Devices ****
card 0: vc4hdmi [vc4-hdmi], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: Device [USB Audio Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

With multiple audio devices, like in the example above, create alsa config file
that will define which is the default. Create file `/etc/asound.conf` and put
there
```
defaults.pcm.card 1
defaults.ctl.card 1
```
(replace `1` with the card ID, from the previous example, that you want to
use.)
