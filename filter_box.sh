# filter bounding box given a BBox-label file

cat "$1" | awk '{
	if( length $2 > 0 )
	{
		if (($4 - $2) * ($3 - $1) > 10000) print $0
	}else
	{
		print $0;
	}
}'
