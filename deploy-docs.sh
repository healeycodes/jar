python3 framework/cli.py build examples/docs

# project packages must be installed locally so they are bundled correctly when deployed
cd examples/docs && pip3 install -r requirements.txt --target . && cd ../..
cd build && vercel --prebuilt --prod && cd ..
