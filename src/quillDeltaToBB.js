const BBCodes = {
     bold: '[B]{res}[/B]',
     italic: '[I]{res}[/I]',
     underline: '[U]{res}[/U]',
     strikethrough: '[S]{res}[/S]',
     color: '[color="{color}"]{res}[/color]',
};

function toBB(op) {
    let res = op.insert;
    for (let attr in op.attributes){
         if (attr in BBCodes){
             // console.log('aaa');
             res = BBCodes[attr].replace('{'+attr+'}',op.attributes[attr]).replace('{res}',res);
         }
    }
    return res;
}

export default {
    deltaToBB(delta){
        let BB = '';
        for (let count in delta.ops) {
            let op = delta.ops[count];
            let block = op.insert;
            BB = BB + toBB(op);
        }
        return BB;
    }
}
