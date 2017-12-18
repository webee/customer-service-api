-- 路径匹配目标
CREATE OR REPLACE FUNCTION path_match_target(type text, path text, target text) RETURNS BOOLEAN AS $$
    BEGIN
        RAISE NOTICE 'path_match_target: %, %, %', type, path, target;
        return case type when 'super' then path like target||'%'
                when 'self' then path = target
                when 'sub' then target like path||'%'
                when 'all' then path like target||'%' or target like path||'%'
                else false
            end;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 单scope匹配目标
CREATE OR REPLACE FUNCTION scope_match_target(scope json, target text) RETURNS BOOLEAN AS $$
    BEGIN
        return path_match_target(scope->>'type', scope->>'path', target);
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配目标
CREATE OR REPLACE FUNCTION scopes_match_target(scopes json, target text) RETURNS BOOLEAN AS $$
    DECLARE
        scope record;
    BEGIN
        for scope in select * from json_to_recordset(scopes) as (type text, path text)
        loop
            if path_match_target(scope."type", scope."path", target) then
                return true;
            end if;
        end loop;
        return false;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配单context路径
CREATE OR REPLACE FUNCTION scopes_match_ctx_path(scopes json, uid text, type text, path text) RETURNS BOOLEAN AS $$
    BEGIN
--         RAISE NOTICE 'scopes_match_ctx_path: %, %, %, %', scopes, uid, type, path;
        return case type when 'self' then scopes_match_target(scopes, path) or scopes_match_target(scopes, path||'.'||uid)
                    when 'sub' then scopes_match_target(scopes, path||'.'||uid)
                    else false
        end;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配单context
CREATE OR REPLACE FUNCTION scopes_match_ctx(scopes json, uid text, ctx json) RETURNS BOOLEAN AS $$
    BEGIN
        return scopes_match_ctx_path(scopes, uid, ctx->>'type', ctx->>'path');
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配多context
CREATE OR REPLACE FUNCTION scopes_match_ctxes(scopes json, uid text, ctxes json) RETURNS BOOLEAN AS $$
    DECLARE
        ctx record;
    BEGIN
        for ctx in select * from json_to_recordset(ctxes) as (type text, path text)
        loop
            if scopes_match_ctx_path(scopes, uid, ctx."type", ctx."path") then
                return true;
            end if;
        end loop;
        return false;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;



-- 单scope匹配目标
CREATE OR REPLACE FUNCTION x_scope_match_target(scope text[], target text) RETURNS BOOLEAN AS $$
    BEGIN
        return path_match_target(scope[1], scope[2], target);
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配目标
CREATE OR REPLACE FUNCTION x_scopes_match_target(scopes text[][], target text) RETURNS BOOLEAN AS $$
    DECLARE
        scope text[];
    BEGIN
        foreach scope slice 1 in array scopes
        loop
            if path_match_target(scope[1], scope[2], target) then
                return true;
            end if;
        end loop;
        return false;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配单context路径
CREATE OR REPLACE FUNCTION x_scopes_match_ctx_path(scopes text[][], uid text, type text, path text) RETURNS BOOLEAN AS $$
    BEGIN
        RAISE NOTICE 'scopes_match_ctx_path: %, %, %, %', scopes, uid, type, path;
        return case type when 'self' then x_scopes_match_target(scopes, path) or x_scopes_match_target(scopes, path||'.'||uid)
                    when 'sub' then x_scopes_match_target(scopes, path||'.'||uid)
                    else false
        end;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配单context
CREATE OR REPLACE FUNCTION x_scopes_match_ctx(scopes text[][], uid text, ctx text[]) RETURNS BOOLEAN AS $$
    BEGIN
        return x_scopes_match_ctx_path(scopes, uid, ctx[1], ctx[2]);
    END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 多scopes匹配多context
CREATE OR REPLACE FUNCTION x_scopes_match_ctxes(scopes text[][], uid text, ctxes text[][]) RETURNS BOOLEAN AS $$
    DECLARE
        ctx text[];
    BEGIN
        foreach ctx slice 1 in array ctxes
        loop
            if x_scopes_match_ctx_path(scopes, uid, ctx[1], ctx[2]) then
                return true;
            end if;
        end loop;
        return false;
    END;
$$ LANGUAGE plpgsql IMMUTABLE;
