#!/bin/sh
cd blog
make clean
make html
cp -R output/* ../out/
