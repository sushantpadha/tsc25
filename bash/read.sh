#!/usr/bin/env bash
f="lorem.txt"

echo "-------------- read -r --------------"

while read -r line; do
	echo "[LINE]: $line"
done < "$f"

echo
echo "-------------- IFS= read -r --------------"

while IFS= read -r line; do
	echo "[LINE]: $line"
done < "$f"

echo
echo "-------------- IFS= read -r -d' ' --------------"

while IFS= read -r -d' ' line; do
	echo "[LINE]: $line"
done <<< "$(head -n 1 $f)"

echo
echo "-------------- read -r -d';' --------------"

while read -r -d';' line; do
	echo "[LINE]: $line"
done < "$f"

