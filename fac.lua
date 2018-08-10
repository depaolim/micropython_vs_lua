-- ./lua-5.3.5/src/lua fac.lua 

function factorial(n)
    if n == 0 then
        return 1
    end
        return n * factorial(n - 1)
end

print(factorial(4))
