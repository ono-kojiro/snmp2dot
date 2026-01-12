#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

ret=0
agent=""
mibs=""
mibdirs=""

while [ "$#" -ne 0 ]; do
  case "$1" in
    -h | --help)
      usage
      exit 1
      ;;
    -a | --agent)
      shift
      agent=$1
      ;;
    -m | --mibs)
      shift
      mibs=$1
      ;;
    -M | --mibdirs)
      shift
      mibdirs=$1
      ;;
    --oid)
      shift
      oid="$1"
      ;;
    *)
      break
      ;;
  esac

  shift
done

if [ -z "$agent" ]; then
  echo "ERROR: no agent option" 1>&2
  ret=`expr $ret + 1`
fi

if [ -z "$mibs" ]; then
  mibs="ALL"
fi

if [ -z "$mibdirs" ]; then
  mibdirs="/usr/share/snmp/mibs"
fi

if [ "$ret" -ne 0 ]; then
  exit $ret
fi

# read agent config
if [ ! -e "${agent}.shrc" ]; then
  echo "ERROR: no config file, ${agent}.shrc" 1>&2
  ret=`expr $ret + 1`
fi

if [ "$ret" -ne 0 ]; then
  exit $ret
fi

rcfiles=""
rcfiles="${rcfiles} ./common.shrc"
rcfiles="${rcfiles} ./password.shrc"
rcfiles="${rcfiles} ./${agent}.shrc"

ipaddr=""

for rcfile in ${rcfiles}; do
  if [ -e "${rcfile}" ]; then
    echo "INFO: read config from ${rcfile}" 1>&2
    . ${rcfile}
  else
    echo "WARN: config file ${rcfile} not found" 1>&2
  fi
done

if [ -z "${ipaddr}" ]; then
  echo "ERROR: ipaddr variable not found in config files" 1>&2
  exit 1
fi

agent_ip="${ipaddr}"

flags=""
flags="$flags -v $snmpver"

flags="$flags -l $seclevel"
flags="$flags -u $secname"
flags="$flags -a $authprotocol"
flags="$flags -A $authpassword"
flags="$flags -x $privprotocol"
flags="$flags -X $privpassword"

# Display table indexes in a more "program like" output
flags="$flags -OX"

flags="$flags -m $mibs"
flags="$flags -M $mibdirs"
flags="$flags -Pe"
flags="$flags --hexOutputLength=0"

cmd="snmpwalk ${flags} ${agent_ip} ${oid}"
echo "# CMD: $cmd"
$cmd

