# 1. get original_image and original labels
while true; do
	read -p "Where are the original images?" image_path
	if [ -d "$image_path" ]; then break; fi;
	echo "$image_path is not a directory. Check your input and try again!";
done

while true; do	
	read -p "Where are the original labels?" label_path
	if [ -d "$label_path" ]; then break; fi;
	echo "$label_path is not a directory. Check your input and try again!";
done

green_echo()
{
	echo '\033[0;32m'$1'\033[0m';
}
red_echo()
{
	echo '\033[0;31m'$1'\033[0m';
}

# 2. check image-label consistency
labels=$(ls $label_path | grep .txt | tr -d '\n' | sed 's/\(\.txt\)/\1\t/g');
images=$(ls $image_path | grep .jpg | tr -d '\n' | sed 's/\(\.txt\)/\1\t/g');

# 3. ask for training / validation partition ratio
total=$(echo $labels | wc -w);
printf "there are %s labels(s) in total\n" $total;

echo "removing empty labels..."
for l in $labels; do
	if [ $(cat $label_path/$l | wc -l) -eq 0 ]; then
		echo "$label_path/$l is empty, removing..."
		rm "$label_path/$l"
		if [ -f $image_path/$l ]; then
			echo "removing corresponding image..."
			rm "$image_path/$l"
		fi
	fi
done
green_echo "done";

while true; do
	read -p "How many percent of the dataset should be used to validate? (Input should range from 0 to 1)" per
	if [ $(echo "$per>0" | bc -l) -a $(echo "$per<1" | bc -l) ]; then break; fi
	red_echo "Please input floating points between 0 and 1"
done

train_num=$(echo "$per*$total" | bc -l | sed 's/\..*$//');
green_echo "$train_num images will be used for validation";

#4. split images
while true; do
	read -p "Choose the base path where the training data will write" basepath
	if [ -d $bashpath ]; then break; fi
	red_echo "$basepath is not a directory. Please try again.";
done
# remove trailing slash to prevent error
basepath=$(echo $basepath | sed 's/\/$//');
targets="train_images train_labels val_images val_labels"
# check if the propsed names collide with the existing directories
for t in $targets; do
	if [ -d "$basepath/$t" ] ; then
		while true; do
			read -p "$basepath/$t already exists, please choose a name to replace $t" newp
			if [ ! -d "$basepath/$newp" ] ; then 
				echo $targets | sed "s/$t/$newp/" | read targets;
				break
			fi
			red_echo "$basepath/$newp also exists already!"
		done
	fi
done
# create directories
for t in $targets; do
	echo "Making directory $basepath/$t ..."
	mkdir -p "$basepath/$t";
	green_echo "done!"
done
echo "Splitting dataset..."
vals=$(ls $label_path | sort | head -$train_num);
val_num=$(echo $total-$train_num | bc -l | sed 's/\..*$//');
trains=$(ls $label_path | sort | tail -$val_num);
# TODO: copy images and label to folder. Know how to split string by delimiter, then follow the order train_im,train_lb,val_im,val_lb to copy files to corresponding folder
i=0;
for f in targets; do
	case i in
	0|2)
		for tr_im in $trains; do
			echo "$image_path/$tr_im -> $basepath/$f";
			cp $image_path/$tr_im $basepath/$f;
		done
	;;

	1|3)
		for tr_lb in $trains; do
			echo "$label_path/$tr_lb -> $basepath/$f";
			cp $label_path/$tr_lb $basepath/$f;
		done
	;;

	*)
		red_echo "Errors occured... exiting";
		exit;
	;;
	esac
	((var++))
done
green_echo "done!"
