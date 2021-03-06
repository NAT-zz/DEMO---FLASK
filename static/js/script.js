// hàm gọi api
function addToCart(id, name, price){
    fetch("/api/add-item-cart", 
    { 
        method: "POST", 
        body: JSON.stringify(
            {
                "product_id": id,
                'product_name': name,
                'product_price': price
                }), 
        headers: { 'Content-Type': 'application/json'}
    })
    .then(function(res) {
        console.info(res);
        return res.json() 
    }).then(function(data) {
        console.info(data);
        // lấy một thành phần trên html
        // couter đại diện cho nguyên vùng số lượng sản phẩm
        let counter = document.getElementById("cartCounter")
        if (counter !== null)
            counter.innerText = data.total_quantity
    })
}

function updateCartItem(obj, productId)
{
    fetch("/api/update-cart-item", 
    {
        method : "put",
        body: JSON.stringify({
            "product_id" : productId,
            "quantity" : parseInt(obj.value)
        }),
        headers: { 
            'Content-Type': 'application/json'
        } 
    }).then(function(res){
        return res.json()
    }).then(function(data){
        if (data.error_code == 200){
            let quantity= document.getElementById("cart_quantity")
            let amount = document.getElementById("cart_amount")
            let d = data.cart_stats
            if (quantity !== null && amount !==null){
                quantity.innerText = d.total_quantity
                amount.innerText = d.total_amount
            }
            let counter = document.getElementById("cartCounter")
            if (counter !== null)
                counter.innerText = d.total_quantity
        }
        else{
            alert("Cap nhat that bai")
        }
    })
}

function deleteCartItem(productId){
    if (confirm("Ban co chac chan xoa item nay khong: ") == true)
    {
        fetch("/api/delete-cart-item/" + productId, 
        {
            method : "delete"
        }).then(function(res){
            return res.json()
        }).then(function(data){
            if (data.error_code == 200){
                let quantity= document.getElementById("cart_quantity")
                let amount = document.getElementById("cart_amount")
                let d = data.cart_stats
                if (quantity !== null && amount !==null){
                    quantity.innerText = d.total_quantity
                    amount.innerText = d.total_amount

                    //location.reload()
                    let row = document.getElementById("product"+productId)
                    row.style.display = "none"
                }
                let counter = document.getElementById("cartCounter")
                if (counter !== null)
                    counter.innerText = d.total_quantity
            }
            else{
                alert("Xoa that bai")
            }
        })
    }
}
function pay(){
    if (confirm("Ban co muon thanh toan khong: ") == true)
    {
        fetch("/api/pay", { 
            method: 'post'
        }).then(function(res){
                return res.json()
        }).then(function(data){
            if(data.error_code == 200)
                location.reload()
            else 
                alert("THANH TOAN DANG CO LOI")
        })
    }
}