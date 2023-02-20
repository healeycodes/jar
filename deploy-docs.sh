python3 framework/cli.py build examples/docs
# this needs to run once but I've commented it out for my convenience
# cd examples/docs && pip3 install -r requirements.txt --target . && cd ../..
cd build && vercel --prebuilt --prod && cd ..
