#!/bin/bash

set -e

# void, alpine, arch, and suse have packages
# need to build on fedora (without terra) and debian/ubuntu

ROOT=$(pwd)

# fancy color
printf "\033[94m"

if [ -f /usr/bin/apt ]; then
	distro="deb"
elif [ -f /usr/bin/zypper ]; then
	distro="suse"
elif [ -f /usr/bin/pacman ]; then
	distro="arch"
elif [ -f /usr/bin/dnf4 ]; then
	distro="fedora"
elif [ -f /sbin/apk ]; then
	distro="alpine"
elif [ -f /bin/xbps-install ]; then
    distro="void"
elif grep 'ID=nixos' /etc/os-release; then
	echo "NixOS is not supported by this script."
	echo "Bailing out..."
	exit 1
fi

if [ -f /usr/bin/sudo ]; then
	privesc="sudo"
elif [ -f /usr/bin/doas ]; then
	privesc="doas"
fi

echo "Installing, this may take some time...."

# Fedora with the terra repo (Ultramarine) has keyd packaged
[ "$distro" = "fedora" ] && dnf4 info keyd -y&>> pkg.log && FEDORA_HAS_KEYD=1

if [ -z "$(which keyd 2>/dev/null)" ]; then
    # if keyd isnt installed
	echo "Installing keyd dependencies"
	case $distro in
		deb)
			$privesc apt install -y build-essential git &>> pkg.log
			;;
		fedora)
			[ ! "$FEDORA_HAS_KEYD" = "1" ] && $privesc dnf4 groupinstall -y "Development Tools" "Development Libraries" &>> pkg.log
			;;
	esac

	echo "Installing keyd"
	case $distro in
		suse)
			$privesc zypper --non-interactive install keyd &>> pkg.log
			;;
		arch)
			$privesc pacman -S --noconfirm keyd &>> pkg.log
			;;
		alpine)
			$privesc apk add --no-interactive keyd &>> pkg.log
			;;
		void)
		    $privesc xbps-install -S keyd -y &>> pkg.log
			;;
		*)
			if [ "$FEDORA_HAS_KEYD" = "1" ]; then
				$privesc dnf4 install -y keyd &>> pkg.log
			else
				git clone https://github.com/rvaiya/keyd &>> pkg.log
				cd keyd
				make &>> pkg.log
				$privesc make install
				cd ..
			fi
			;;
	esac
fi

echo "Generating config"
# Handle any special cases
if (grep -E "^(Nocturne|Atlas|Eve)$" /sys/class/dmi/id/product_name &> /dev/null)
then
	cp configs/cros-pixel.conf cros.conf
	$privesc mkdir -p /etc/udev/hwdb.d/
	$privesc cp configs/61-pixel-keyboard.hwdb /etc/udev/hwdb.d/
	$privesc udevadm hwdb --update
	$privesc udevadm trigger
elif (grep -E "^(Sarien|Arcada)$" /sys/class/dmi/id/product_name &> /dev/null)
then
	cp configs/cros-sarien.conf cros.conf
else
	printf "By default, the top row keys will do their special function (brightness, volume, browser control, etc).\n"
	printf "Holding the search key will make the top row keys act like fn keys (f1, f2, f3, etc).\n"
	printf "Would you like to invert this? (y/N) "
	read -r INVERT
	[[ $INVERT =~ ^[Yy]$ ]] && python3 cros-keyboard-map.py -i || python3 cros-keyboard-map.py
fi

echo "Installing config"
$privesc mkdir -p /etc/keyd
$privesc cp cros.conf /etc/keyd

echo "Enabling keyd"
case $distro in
    alpine)
	# Chimera uses apk like alpine but uses dinit instead of openrc
	if [ -f /usr/bin/dinitctl ]; then
		$privesc dinitctl start keyd
		$privesc dinitctl enable keyd
	else
        	$privesc rc-update add keyd
        	$privesc rc-service keyd restart
	fi
	;;
	void)
	if [ -f /usr/bin/sv ]; then
	    $privesc ln -s /etc/sv/keyd /var/service
		$privesc sv enable keyd
		$privesc sv start keyd
	else
	       echo "This script can only be used for Void Linux using 'runit' init system. Other init system on Void Linux are currently unsupported."
		   echo "I'M OUTTA HERE!"
		   exit 1
	fi
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
# reset color
printf "\033[0m"
