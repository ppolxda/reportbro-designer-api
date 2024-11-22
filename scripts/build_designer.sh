SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/..
# echo $SCRIPTPATH
cd $SCRIPTPATH/reportbro-designer

if [ ! -e "$SCRIPTPATH/reportbro-designer/node_modules" ]; then
    npm install
fi
npm run build-prod
rm -rf $SCRIPTPATH/reportbro_designer_api/static/reportbro/*
cp -r $SCRIPTPATH/reportbro-designer/dist/* $SCRIPTPATH/reportbro_designer_api/static/reportbro
