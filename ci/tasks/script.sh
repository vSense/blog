#!/bin/sh
cd blog
make clean
make html
cp -R output/* ../out/
tar -zcvf ../out/blog.tgz ../out/*
