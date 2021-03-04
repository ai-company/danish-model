rm -rf ./out
echo "Step 1/3"
mkdir ./out
grep -v " '[^ ]" ./formatted.txt | \
grep -v \'\ s\   | \
grep -v \'\ ll\  | \
grep -v \'\ ve\  | \
grep -v \'\ m\   > step1.txt
echo "Step 2/3"
python preprocess.py step1.txt step2.txt
echo "Step 3/3"
head -n -400000 step2.txt > ./out/ep.train.txt
tail -n 400000 step2.txt > step3.txt
head -n -200000 step3.txt > ./out/ep.dev.txt
tail -n 200000 step3.txt > ./out/ep.test.txt
echo "Cleaning up temporary files..."
rm -f step1.txt step2.txt step3.txt