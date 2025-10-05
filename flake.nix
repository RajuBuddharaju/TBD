{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils, ... }@inputs:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          config.cudaSupport = true;
        };

        jupyterlab-vim = pp: with pp;
          buildPythonPackage rec {
            pname = "jupyterlab-vim";
            version = "4.1.4";
            format = "wheel";

            src = fetchPypi {
              inherit version format;
              pname = "jupyterlab_vim";
              python = "py3";
              dist = "py3";
              hash = "sha256-E8Kf8f04X93zPrhaixZEG+acYgMocLuXowVLLPAKsTU=";
            };

            propagatedBuildInputs = [
              jupyterlab
            ];
          };


        torchcodec = pp: with pp; with pkgs; 
          buildPythonPackage {
            pname = "torchcodec";
            version = "0.7.0";
            pyproject = true;

            stdenv = torch.stdenv;

            src = fetchFromGitHub {
              owner = "meta-pytorch";
              repo = "torchcodec";
              tag = "v0.7.0";
              hash = "sha256-zPPyBY/SHyJBFm/KRJFrlli4kswfSkEgLqR+/n6cFBk=";
            };

            propagatedBuildInputs = [
              ffmpeg
            ];

            nativeBuildInputs = with cudaPackages; [
              pkg-config
              cmake
              cuda_nvcc
              nccl
            ];

            buildInputs = with cudaPackages; [
              libnpp
              cuda_cudart
              cuda_nvrtc
            ];

            dependencies = [
              numpy
              torch
            ];

            env = {
              # BUILD_AGAINST_ALL_FFMPEG_FROM_S3 = 0;
              CUDA_TOOLKIT_ROOT_DIR = "${pkgs.cudatoolkit}";
              FORCE_CUDA = 1;
            };

            doCheck = false;

            pythonImportsCheck = [ "torchcodec" ];

            nativeCheckInputs = [
              pytest
              writableTmpDirAsHomeHook
            ];

            checkPhase = ''
              py.test test --ignore=test/test_datasets_download.py
            '';
          };
        python = pkgs.python3.withPackages
          (pp: with pp; [
            # Python + Jupyter
            jupyter
            jupyterlab
            (jupyterlab-vim pp)
            ipython
            tqdm

            # Data manipulation and visualisation
            numpy
            pandas
            matplotlib
            seaborn

            # ML
            scikit-learn
            statsmodels
            faster-whisper

            torchWithCuda
            torchaudio
            sentencepiece
            # (torchcodec pp)
            ultralytics
            onnx
            datasets
            evaluate
            transformers
            diffusers
            accelerate
            hf-xet

            # NLP
            nltk
            num2words
            emoji
            wikipedia

            flask
            mistral-common
            pydantic
          ]);

        packages = with pkgs; [
          pyright
          python
          nodejs
        ];

      in {
        devShells.default = pkgs.mkShell {
          inherit packages;
        };
      }
    );
}

