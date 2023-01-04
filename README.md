# radio-box

CLI tool for Internet Radio streaming

This tool provides command line and Web interface to stream pre-configured
Internet radios. It is meant to be useful on devices that have audio output
but are running a headless operating system. For example a Raspberry Pi
running linux server.

---
**NOTE**

This tool does not come with any internet radios pre-configured. You'll have
to dig around for the direct stream links of your favorite radios and configure
them manually.

---

## Installation (Snap)

`radio-box` is currently published as a snap, and it's also the easiest way to
get it installed.

```shell
sudo snap install radio-box
# In order for audio playback to work, an "alsa" interface needs to be manually connected
sudo snap connect radio-box:alsa
```

## Usage (Snap)

To get `radio-box` going, you'll have to configure streaming links to the radios
that you want to listen to. Open the configuration file at

```
/var/snap/radio-box/current/config/radio-box.yaml
```

with a text editor of your choice and populate the `stations` dictionary.
The config is a `yaml` file, so it really helps if you understand its
format, but even if not, there's already an example configuration with comments
that can help you get started.

After configuration change, it's necessary to restart `radio-box` services with

```shell
sudo snap restart radio-box
```

And that's about it. By default, the web interface listens on every interface
on the device, on port `80`, so you can open

```
http://<your_device_ip>:80/
```

and you should be greeted with web interface that allows you to select one of
the pre-configured stations and start/stop its audio stream.

## Configuration (Snap)

Configuration file for the snap version is located at 

```
/var/snap/radio-box/current/config/radio-box.yaml
```

and look generally something like this:
```yaml
socket: "/var/snap/radio-box/common/run/radio-box.pipe"

stations:
  first_radio:  # machine-friendly name (ID)
    url: "https://radio1.example.org/stream.mp3" # direct streaming link
    name: "My Favorite Radio"  # human friendly name
  second_radio:  # machine-friendly name (ID)
    url: "https://radio2.example.org/stream.mp3" # direct streaming link
    name: "My Second Favorite Radio"  # human friendly name
```

This file is generally only used to add/remove/edit radio stations in the field
`stations`. Don't change the `socket` option unless you really need to because
if the location of the socket is not writable by the `radio-box` process, the
service will stop working.

After every change to the config file it's required to restart `radio-box`
services with

```shell
sudo snap restart radio-box
```

You can also change properties of the web interface directly via snap
configuration. To see current values you can run

```shell
sudo snap get radio-box
```

Example output:
```
Key      Value
address  0.0.0.0
port     80
workers  4
```

To change these values you can use
```
sudo snap set <option_name> <value>
```

For example if your port `80` is already occupied, and you want the web
interface to listen on different port, you can run

```shell
sudo snap set port 8080
```

Details about the exposed config options:
* **address** - Address on which the web interface is listening. Default is
  `0.0.0.0` which means every available interface on the device.
* **port** - Port on which the web interface is listening. Default is `80`
* **workers** - Number of parallel workers that handle web requests. Default
  is `4`.

## Debugging (Snap)

`radio-box` consists of two services
* *web-service* - Runs server with web interface and REST api.
* *stream-service* - Plays selected audio stream via connected audio device

You can check the state of these services with systemd

```shell
# Check web service status
systemctl status snap.radio-box.web-service
# Check streaming service status
systemctl status snap.radio-box.stream-service
```

If something goes wrong, you can access log files of these services with
journalctl

```shell
# Web service logs
journalctl -feu snap.radio-box.web-service
# Streaming service logs
journalctl -feu snap.radio-box.stream-service
```

## Manual deployment

**WIP:** Full manual deployment guide is not yet finished.

This is a more complicated path, but it might be necessary if your device/OS
does not support snaps, or if you want to set up a development environment.
Following steps should get you started with a fresh installation.

Before starting, make sure that the user that'll be running `radio-box` is in
the `audio` group.
```shell
sudo usermod -a -G audio <username>
```
This change takes effect only in new sessions, so to be safe, logout and
login again.

Now the dependencies:
```shell
sudo apt install --no-install-recommends vlc-bin vlc-plugin-base
sudo apt install alsa-base tinyproxy
```

---
**NOTE**

Option `--no-install-recommends` is required on headless system to ensure
that entire desktop environment is not installed by `vlc-plugin-base` package.

---

Verify that `alsa` detects your sound card by running
```shell
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

**WIP:** Rest of the manual deployment guide is not finished.

## TODO

Features I'd like to implement in future:
* Support for audio output via bluetooth
* Ability to add/remove/edit radio stations directly via web interface