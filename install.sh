#!/bin/bash

#alpine arch and suse have packages
#need to build on fedora and deb*

ROOT=$(pwd)

if [ -f /usr/bin/apt ]; then
	distro="deb"
elif [ -f /usr/bin/zypper ]; then
	distro="suse"
elif [ -f /usr/bin/pacman ]; then
	distro="arch"
elif [ -f /usr/bin/dnf ]; then
	distro="fedora"
elif [ -f /usr/bin/apk ]; then
	distro="alpine"
fi

if [ -f /usr/bin/sudo ]; then
	privesc="sudo"
elif [ -f /usr/bin/doas ]; then
	privesc="doas"
fi


if ! [ -f /usr/bin/keyd ]; then
    # if keyd isnt installed
	echo "Installing keyd dependencies"
	case $distro in
		deb)
			$privesc apt install -y build-essential git
			;;
		arch)
			$privesc pacman -S --noconfirm base-devel git
			;;
		fedora)
			$privesc dnf groupinstall -y "Development Tools" "Development Libraries"
			;;
	esac

	echo "Installing keyd"
	case $distro in
		suse)
			$privesc zypper --non-interactive install keyd
			;;
		arch)
			git clone https://aur.archlinux.org/keyd.git
			cd keyd
			makepkg -si --noconfirm
			cd ..
			;;
		alpine)
			$privesc apk add --no-interactive keyd
			;;
		*)
			git clone https://github.com/rvaiya/keyd
			cd keyd
			make
			$privesc make install
			cd ..
			;;
	esac
fi

echo "Generating config"
# Handle any special cases
if (grep -E "^(Nocturne|Atlas|Eve)$" /sys/class/dmi/id/product_name &> /dev/null)
then
	cp configs/cros-pixel.conf cros.conf
else
	python3 cros-keyboard-map.py
fi

echo "Installing config"
$privesc mkdir -p /etc/keyd
$privesc cp cros.conf /etc/keyd

echo "Enabling keyd"
case $distro in
    alpine)
        $privesc rc-update add keyd
        $privesc rc-service keyd restart
	;;
    *)
        $privesc systemctl enable keyd
	$privesc systemctl restart keyd
	;;
esac

echo "Installing libinput configuration"
$privesc mkdir -p /etc/libinput
if [ -f /etc/libinput/local-overrides.quirks ]; then
    cat $ROOT/local-overrides.quirks | $privesc tee -a /etc/libinput/local-overrides.quirks > /dev/null
else
    $privesc cp $ROOT/local-overrides.quirks /etc/libinput/local-overrides.quirks
fi

echo "Done"
