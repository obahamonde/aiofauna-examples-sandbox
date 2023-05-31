docker build -t test_kube . --wait
docker images | grep test_kube
docker tag test_kube gcr.io/steam-patrol-380019/test_kube
docker push gcr.io/steam-patrol-380019/test_kube