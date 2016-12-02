dir="$1";
cr="$2";
cg="$3";
cb="$4";
min_area=90;

mkdir -p bbox;
for fn in `ls $dir`; do
	printf 'processing %s...' "$fn";
	name=`echo "$fn" | sed 's/\..*$/\.txt/'`
	res=$(python box.py "$dir/$fn" $cr $cg $cb 90 0.5 | tee "$name" | grep gg);
	if [ ! -z "$res" ]; then 
		rm "$name";
	else
		count=$(cat "$name" | awk '{if(length($2) > 0)print $0}' | wc -l)
		if [ "$count" -eq 0 ]; then
			printf 'no objects found...'
			rm "$name";
		else
			printf '%s object(s) found!' "$count"
			mv "$name" bbox;
		fi
		
	fi;
	echo done
done

