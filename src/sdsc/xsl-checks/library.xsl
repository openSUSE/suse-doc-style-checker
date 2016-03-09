<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:db5="http://docbook.org/ns/docbook"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:py="https://www.github.com/openSUSE/suse-doc-style-checker"
  xmlns:exslt="http://exslt.org/common"
  exclude-result-prefixes="db5 xlink py exslt">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <xsl:template match="*|db5:*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text()"/>

  <xsl:template match="/">
    <part>
      <xsl:attribute name="source"><xsl:apply-templates mode="part-source"/></xsl:attribute>
      <part-title><xsl:apply-templates mode="part-title"/></part-title>
      <xsl:apply-templates/>
    </part>
  </xsl:template>

  <xsl:template match="*|db5:*" mode="part-source">FIXME</xsl:template>

  <xsl:template name="sourcehint">
    <xsl:param name="node" select="."/>
    <location>
      <xsl:call-template name="file"/>
      <xsl:call-template name="withinid"/>
      <line><xsl:value-of select="py:linenumber()"/></line>
    </location>
  </xsl:template>

  <xsl:template name="file">
    <xsl:param name="node" select="."/>
    <xsl:variable name="candidate">
      <xsl:call-template name="file-nomarkup">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="string-length($candidate) &gt; 0">
      <file><xsl:value-of select="$candidate"/></file>
    </xsl:if>
  </xsl:template>

  <xsl:template name="withinid">
    <xsl:param name="node" select="."/>
    <xsl:variable name="candidate">
      <xsl:call-template name="withinid-nomarkup">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="string-length($candidate) &gt; 0">
      <withinid><xsl:value-of select="$candidate"/></withinid>
    </xsl:if>
  </xsl:template>

  <xsl:template name="file-nomarkup">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/ancestor-or-self::*[@xml:base]|$node/ancestor-or-self::db5:*[@xml:base]">
      <xsl:value-of select="$node/ancestor-or-self::*[@xml:base][1]/@xml:base|$node/ancestor-or-self::db5:*[@xml:base][1]/@xml:base"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="withinid-nomarkup">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/ancestor-or-self::*[@id]|$node/ancestor-or-self::db5:*[@xml:id]">
      <xsl:value-of select="$node/ancestor-or-self::*[@id][1]/@id|$node/ancestor-or-self::db5:*[@xml:id][1]/@xml:id"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="createid">
    <xsl:param name="use-url-attribute" select="0"/>
    <xsl:param name="use-function-attribute" select="0"/>
    <xsl:param name="use-fileref-attribute" select="0"/>
    <xsl:param name="node" select="."/>

    <xsl:choose>
      <xsl:when test="$node/@id|$node/@xml:id">
        <id><xsl:value-of select="$node/@id|$node/@xml:id"/></id>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$node/title">
            <name><xsl:value-of select="normalize-space($node/title)"/></name>
          </xsl:when>
          <xsl:when test="$use-url-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@url|$node/@xlink:href)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@url|$node/@xlink:href), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@url|$node/@xlink:href)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:when test="$use-function-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@function)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@function), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@function)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:when test="$use-fileref-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@fileref)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@fileref), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@fileref)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="safecharacters">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input,
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ?:;,!@#$%^§&amp;&lt;&gt;äàâãáåæÄÀÂÃÁÆÅçÇðÐèêéëËÉÈÊìîïíÍÏÌÎñÑòôõóöøœŒØÖÓÒÔÕùûüúÚÜÙÛýÿÝß©¢®þÞµ°[]“”{}|()= ',
      '')"/>
  </xsl:template>

  <xsl:template name="safecharacters-AZ">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '')"/>
  </xsl:template>

  <xsl:template name="safecharacters-special">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input,
      '?:;,!@#$%^§&amp;&lt;&gt;äàâãáåæÄÀÂÃÁÆÅçÇðÐèêéëËÉÈÊìîïíÍÏÌÎñÑòôõóöøœŒØÖÓÒÔÕùûüúÚÜÙÛýÿÝß©¢®þÞµ°[]“”{}|()= ',
      '')"/>
  </xsl:template>

  <xsl:template name="change-case">
    <xsl:param name="text" select="'?'"/>
    <xsl:param name="case" select="'lower'"/>
    <xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
    <xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>

    <xsl:choose>
      <xsl:when test="case = 'upper'">
        <xsl:value-of select="translate($text,$lower,$upper)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="translate($text,$upper,$lower)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Template that starts terminology check. -->
  <xsl:template match="para|title|entry|db5:para|db5:title|db5:entry" mode="terminology">
    <xsl:choose>
      <xsl:when test="(self::entry or self::db5:entry) and (para or db5:para)">
        <xsl:apply-templates mode="terminology"/>
      </xsl:when>
      <xsl:when test="(ancestor-or-self::*/@role = 'legal') or (ancestor-or-self::db5:*/@role = 'legal')">
        <!-- nothing -->
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="node" select="."/>
        <xsl:variable name="messagetype">
          <xsl:call-template name="messagetype"/>
        </xsl:variable>
        <xsl:variable name="withinid">
          <xsl:call-template name="withinid-nomarkup"/>
        </xsl:variable>
        <xsl:variable name="file">
          <xsl:call-template name="file-nomarkup"/>
        </xsl:variable>
        <xsl:variable name="content-candidate">
          <xsl:apply-templates mode="terminology-content"/>
        </xsl:variable>
        <xsl:variable name="content-pretty-candidate">
          <xsl:apply-templates mode="content-pretty"/>
        </xsl:variable>
        <xsl:variable name="content"><xsl:value-of
          select="normalize-space($content-candidate)"/></xsl:variable>
        <xsl:variable name="content-pretty"><xsl:value-of
          select="normalize-space($content-pretty-candidate)"/></xsl:variable>

        <xsl:copy-of
          select="py:termcheck($termdataid, $content, $content-pretty, $withinid,
                               $file, normalize-space($messagetype))"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*|db5:*" mode="terminology">
    <xsl:apply-templates mode="terminology"/>
  </xsl:template>

  <xsl:template name="messagetype">error</xsl:template>

  <xsl:template match="text()" mode="terminology"/>


  <!-- Replace some elements for terminology checking itself. -->
  <xsl:template match="text()" mode="terminology-content">
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="classname|code|command|computeroutput|constant|envar|
                       exceptionname|filename|function|interfacename|literal|
                       methodname|option|package|parameter|prompt|replaceable|
                       sgmltag|structfield|systemitem|tag|userinput|varname|
                       symbol|keycombo|keycap|menuchoice|guimenu|email|filename|
                       ulink|uri|xref|symbol|inlinemediaobject|citetitle|
                       db5:classname|db5:code|db5:command|db5:computeroutput|
                       db5:constant|db5:envar|db5:exceptionname|db5:filename|
                       db5:function|db5:interfacename|db5:literal|db5:methodname|
                       db5:option|db5:package|db5:parameter|db5:prompt|
                       db5:replaceable|db5:sgmltag|db5:structfield|
                       db5:systemitem|db5:tag|db5:userinput|db5:varname|
                       db5:symbol|db5:keycombo|db5:keycap|db5:menuchoice|
                       db5:guimenu|db5:email|db5:filename|db5:link|db5:uri|
                       db5:xref|db5:symbol|db5:inlinemediaobject|db5:citetitle"
    mode="terminology-content">

    <!-- Find out number of tokens that are included within the element.
         This helps us position of the red underline in errors. -->
    <xsl:variable name="formatted">
      <xsl:apply-templates select="self::*" mode="content-pretty"/>
    </xsl:variable>
    <xsl:variable name="tokens-candidate">
      <xsl:value-of select="py:counttokens($formatted)"/>
    </xsl:variable>
    <xsl:variable name="tokens" select="normalize-space($tokens-candidate)"/>

    <xsl:choose>
      <xsl:when test="self::keycombo|self::keycap|
                      self::db5:keycombo|self::db5:keycap">
        ##@key-<xsl:value-of select="$tokens"/>##
      </xsl:when>
      <xsl:when test="self::menuchoice|self::guimenu|
                      self::db5:menuchoice|self::db5:guimenu">
        ##@ui-<xsl:value-of select="$tokens"/>##
      </xsl:when>
      <xsl:when test="self::email|self::filename|self::ulink|self::uri|
                      self::xref|
                      self::db5:email|self::db5:filename|self::db5:link|
                      self::db5:uri|self::db5:xref">
        ##@ref-<xsl:value-of select="$tokens"/>##
      </xsl:when>
      <xsl:when test="self::inlinemediaobject|self::db5:inlinemediaobject">
        ##@image-<xsl:value-of select="$tokens"/>##
      </xsl:when>
      <xsl:when test="self::citetitle|self::db5:citetitle">
        ##@quote-<xsl:value-of select="$tokens"/>##
      </xsl:when>
      <xsl:otherwise>
        ##@mono-<xsl:value-of select="$tokens"/>##
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Hmm?? -->
  <xsl:template match="remark|indexterm|db5:remark|db5:indexterm"
    mode="terminology-content"/>

  <xsl:template match="*|db5:*" mode="terminology-content">
    <xsl:apply-templates mode="terminology-content"/>
  </xsl:template>


  <!-- Semi-format some elements for terminology check output. -->
  <xsl:template match="*|db5:*" mode="content-pretty">
    <xsl:apply-templates mode="content-pretty"/>
  </xsl:template>

  <xsl:template match="text()" mode="content-pretty">
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="keycap|db5:keycap" mode="content-pretty">
    <xsl:choose>
      <xsl:when test="@function">
        <xsl:choose>
          <xsl:when test="@function = 'alt'">Alt</xsl:when>
          <xsl:when test="@function = 'backspace'">&lt;&#x2014;</xsl:when>
          <xsl:when test="@function = 'command'">&#x2318;</xsl:when>
          <xsl:when test="@function = 'control'">Ctrl</xsl:when>
          <xsl:when test="@function = 'delete'">Del</xsl:when>
          <xsl:when test="@function = 'down'">&#x02193;</xsl:when>
          <xsl:when test="@function = 'end'">End</xsl:when>
          <xsl:when test="@function = 'enter'">Enter</xsl:when>
          <xsl:when test="@function = 'escape'">Esc</xsl:when>
          <xsl:when test="@function = 'home'">Home</xsl:when>
          <xsl:when test="@function = 'insert'">Ins</xsl:when>
          <xsl:when test="@function = 'left'">&#x02190;</xsl:when>
          <xsl:when test="@function = 'meta'">Meta</xsl:when>
          <xsl:when test="@function = 'pagedown'">Page &#x02193;</xsl:when>
          <xsl:when test="@function = 'pageup'">Page &#x02191;</xsl:when>
          <xsl:when test="@function = 'right'">&#x02192;</xsl:when>
          <xsl:when test="@function = 'shift'">Shift</xsl:when>
          <xsl:when test="@function = 'space'">Space</xsl:when>
          <xsl:when test="@function = 'tab'">&#x02192;|</xsl:when>
          <xsl:when test="@function = 'up'">&#x02191;</xsl:when>
          <xsl:otherwise>???</xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates mode="content-pretty"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="keycombo|db5:keycombo" mode="content-pretty">
    <xsl:for-each select="*|db5:*">
      <xsl:if test="position()&gt;1">–</xsl:if>
      <xsl:apply-templates mode="content-pretty" select="."/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="menuchoice|db5:menuchoice" mode="content-pretty">
    <xsl:for-each select="*|db5:*">
      <xsl:if test="position()&gt;1"> &gt; </xsl:if>
      <xsl:apply-templates mode="content-pretty" select="."/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="xref|db5:xref" mode="content-pretty">
      <xsl:value-of select="@linkend"/>
  </xsl:template>

  <xsl:template match="ulink|db5:link" mode="content-pretty">
    <xsl:choose>
      <xsl:when test="text()">
        <xsl:value-of select="."/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@url|@xlink:href"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="remark|indexterm|inlinemediaobject|
                       db5:remark|db5:indexterm|db5:inlinemediaobject"
    mode="content-pretty"/>

</xsl:stylesheet>
