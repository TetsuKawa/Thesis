fn fnc2(a: i32, b: i32) -> i32{
    return a*b
}


fn fnc1(a: i32, b: i32, c: i32) -> i32 {
    let x;
    x = fnc2(a,c);
    return a+b+x;
}

fn main() {
    let a = 1;
    let b = 2;
    let c = 3;
    let _d;
    _d = fnc1(a,b,c);
}
