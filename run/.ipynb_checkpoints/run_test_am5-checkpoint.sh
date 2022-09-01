cd ..
cuda=3
# seedlist=("0" "100")
# for seed in ${seedlist[@]}
# do
#     CUDA_VISIBLE_DEVICES=${cuda} python train_wdgl_w.py --dataset_name AMinerAuthor --k 0 --embedder transformer --encode_type pure --decode_type pure --num_layers 1 --scorer sm --scorer_num_layers 1 --optimizer adam --bs 512 --dropout 0.7 --gamma 0.99 --dim_hidden 64 --lr 0.0001 --dim_edge 128 --dim_vertex 128 --epochs 100 --test_epoch 5 --sampling 40 --evaltype test --fix_seed --seed ${seed} --use_gpu
#     CUDA_VISIBLE_DEVICES=${cuda} python train_wdgl_w.py --dataset_name AMinerAuthor --k 0 --embedder unigcnii --num_layers 2 --scorer sm --scorer_num_layers 1 --optimizer adam --bs 512 --dropout 0.7 --gamma 0.99 --dim_hidden 64 --lr 0.001 --dim_edge 128 --dim_vertex 128 --epochs 100 --test_epoch 5 --sampling 40 --evaltype test --fix_seed --seed ${seed} --use_gpu
# done
CUDA_VISIBLE_DEVICES=${cuda} python train_wdgl_w.py --dataset_name AMinerAuthor --k 0 --embedder transformer --encode_type pure --decode_type pure --num_layers 1 --scorer sm --scorer_num_layers 1 --optimizer adam --bs 512 --dropout 0.7 --gamma 0.99 --dim_hidden 64 --lr 0.0001 --dim_edge 128 --dim_vertex 128 --epochs 100 --test_epoch 5 --sampling 40 --evaltype test --fix_seed --seed 10 --use_gpu
