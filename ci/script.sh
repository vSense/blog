#!/bin/sh
cd blog
make clean
make html
cp -r output/* ../out/
