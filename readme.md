# Install Dependencies

## MacOS
```shell
brew install miniforge

brew install geckodriver

conda env create -f openforge-env-mac.yml

conda activate learner
```

## Linux
```shell
wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz

tar -xvf geckodriver*
chmod +x geckodriver

sudo apt install firefox-geckodriver

conda env create -f openforge-env-linux.yml

conda activate learner
```

## RaspberyPI
```shell
# Install PIGPIOD
sudo apt-get install pigpio python-pigpio python3-pigpio
sudo pigpiod
```


## Installing CUDA
```shell
sudo apt install nvidia-cuda-toolkit
sudo apt install ./libcudnn8_8.2.0.53-1+cuda11.3_amd64.deb
nvidia-smi -l 2
```

# BUG FIXES
- opencv circle tracking fails, if orientation changed
- moved the tracking to virtual env
- velocity and position included
- opencv tracking only assigned for physical env