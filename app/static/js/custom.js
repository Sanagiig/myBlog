/**
 * Created by Sanagi on 2017/7/11.
 */

//follow sb
function follow(el,url,follower,followed){
    if(el.innerText =='关注')
        opt = 'following'
    else if(el.innerText =='取消关注')
        opt = 'unfollow'
    else
        opt = false

    if(opt) {
        $.ajax({
            type: 'POST',
            url: url,
            data: JSON.stringify({
                opt: opt,
                follower: follower,
                followed: followed,
            }),
            success: function (r) {
                if (r.result) {
                    if (opt == 'following') {

                        el.className =  'btn btn-warning';
                        el.innerText = '取消关注';
                    } else {

                        el.className =  'btn btn-success';
                        el.innerText = '关注'
                    }
                } else {
                    alert('由于不可描述的网络原因，操作无效。')
                }
            }
        })
    }
}

//  add_article
function submit_art(user_id,relocation_url){
    document.getElementById('save').onclick = function(){
        var author = document.getElementById('author').value;
        var title = document.getElementById('title').value;
        var status = document.getElementById('status').value;
        var categories = document.getElementById('categories');
        var tags = document.getElementById('tags');
        var content = document.getElementById('content_ifr').contentWindow.document.body.innerHTML
        if(! content)
            content = document.getElementById('content').value
        cats=[]
        ts=[]
        var j=0;
        for(var i=0;i<categories.options.length;i++)
            if(categories.options[i].selected)
                if(categories.options[i].value) {
                    if(j<3){
                        cats.push(categories.options[i].value);
                        j++;
                    }
                }

        j=0
        for(var i=0;i<tags.options.length;i++)
            if(tags.options[i].selected)
                if(tags.options[i].value) {
                    if(j<3){
                        ts.push(tags.options[i].value);
                        j++;
                    }
                }

        $.ajax({
            type:'POST',
            traditional:true,
            data:JSON.stringify({
                user_id:user_id,
                author:author,
                title:title,
                status:status,
                categories:cats,
                tags:ts,
                content:content,
            }),
            success:function(r){
                if(r.result){
                    if(confirm('成功保存文章,是否继续 ？')){
                        putup = document.getElementsByClassName('putup')
                        for(var i=0;i<putup.length;i++)
                            putup[i].value = ''
                        content = document.getElementById('content_ifr')
                        content.contentWindow.document.body.innerHTML = ''
                    }
                    else
                        window.location.href=relocation_url
                }
                else
                    alert('保存失败，请稍后再试。')
            },
            error:function(){alert('你的文章未能正常保存，请检查网络。')}
        })
    }
}
function changeCT(){
        var categories = document.getElementById('categories');
        var tags = document.getElementById('tags');
        var cats_div = document.getElementById('cats_div');
        var tags_div = document.getElementById('tags_div');
        var cats_div_innerhtml = '';
        var tags_div_innerhtml = '';

//{#                获取选中的标签#}
        var j = 0
        for(var i=0;i<categories.options.length;i++)
            if(categories.options[i].selected)
                if(categories.options[i].value){
                    if(j<3){
                        cats_div_innerhtml += '<label class="label-primary" style="font-size: 18px;border-radius: 4px;width: 90px;text-align: center;margin-right: 20px;">'+categories.options[i].value +'</label>'
                        j++;
                    }
                }

        j = 0
        for(var i=0;i<tags.options.length;i++)
            if(tags.options[i].selected)
                if(tags.options[i].value) {
                    if (j < 3) {
                        tags_div_innerhtml += '<label class="label-success" style="font-size: 18px;border-radius: 4px;width: 90px;text-align: center;margin-left: 20px;">' + tags.options[i].value + '</label>'
                        j++;
                    }
                }

        cats_div.innerHTML=cats_div_innerhtml;
        tags_div.innerHTML=tags_div_innerhtml;
    }

// article_list
function del_article(article_id,des_url) {
        $.ajax({
            type: "POST",
            url:des_url,
            data: JSON.stringify({
                opt:'del_article',
                article_id:article_id,
            }),
            success: function (r) {
                if(r.result) {
                    el = document.getElementById('article_row'+article_id);
                    el.parentNode.removeChild(el);
                    alert('删除成功');
                }
                else
                    alert('删除失败 ！')
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('服务器内部错误 ！');
            }
        });
}
function del_articles(ev,des_url){
    ev.stopPropagation()
    arts_id_cb = document.getElementsByClassName('article_cb');
    article_id_list = [];
    for(var i= 0;i<arts_id_cb.length;i++)
        if(arts_id_cb[i].checked)
            article_id_list.push(arts_id_cb[i].value);
     $.ajax({
        type: "POST",
        url:des_url,
        data: JSON.stringify({
            opt:'del_articles',
            articles_id_list:article_id_list,
        }),
        success: function (r) {
            if(r.result) {
                for(var i =arts_id_cb.length -1;i>=0;i--) {
                    if (arts_id_cb[i].checked) {
                        table_row = document.getElementById('article_row'+arts_id_cb[i].value)
                        table_row.parentNode.removeChild(table_row);
                    }
                }
                alert('删除成功');
            }
            else
                alert('删除失败 ！')
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('服务器内部错误 ！');
        }
    });
}
function edit_article(url) {
    location.href = url
}

// change password
function ResetPassword(e){
    e.stopPropagation();
    OldP = document.getElementById('OldPassword');
    NewP= document.getElementById('NewPassword');
    ReTypeP =document.getElementById('RetypePassword');

    if(NewP.value != ReTypeP.value)
        alert('两次输入的新密码不一致~~');

    $.ajax({
        type:'POST',
        data:{
            opt:'resetpassword',
            old_p:OldP.value,
            new_p:NewP.value,
        },
        success: function (r){
            if(r.result){
                OldP.value='';
                NewP.value='';
                ReTypeP.value='';
                alert('修改成功新密码已生效 ！');
            }else{
                alert('修改失败，请确认你输入的密码。')
            }
        }
    })
}