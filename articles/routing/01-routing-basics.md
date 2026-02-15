Between client & server communication or between any server to server communication, there are multiple hiddne hops which called routers, now a days called switches as the modern switches can easily customize to do any function.
Going forward we will refer routers or switches interchangably. 

For this switch to communicate each other it needs to understand some language which is called routing. Now depending on the use-case, the routing language can be different.
If network is too small with small number of hosts <>, like <> , where we need to control things manually, then we can use the static routing only. But it is not scalable for sure.
If network starts to grow, you can use the dynamic routing protocols. The most popular ones that are being used are the open source protocols - OSPF & BGP.
The rest of the chapter will focus on these two protocols and their different applications. 
